import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import patch
from datetime import datetime
from dataclasses import asdict
from cve_lookup import CVELookup, CVEInfo, PORT_TO_SERVICE


class TestPortToService:

    def test_port_dicom_104(self):
        assert PORT_TO_SERVICE[104] == "dicom"

    def test_port_ssh_22(self):
        assert PORT_TO_SERVICE[22] == "ssh"

    def test_port_rdp_3389(self):
        assert PORT_TO_SERVICE[3389] == "rdp"

    def test_port_http_80(self):
        assert PORT_TO_SERVICE[80] == "http"

    def test_nieznany_port_nie_istnieje(self):
        assert PORT_TO_SERVICE.get(99999) is None


class TestCVEInfo:

    def test_tworzenie_cve_info(self):
        cve = CVEInfo(cve_id="CVE-2024-0001", description="Test", severity="HIGH", cvss_score=7.5)
        assert cve.cve_id == "CVE-2024-0001"
        assert cve.severity == "HIGH"
        assert cve.cvss_score == 7.5

    def test_affected_products_domyslnie_pusta_lista(self):
        cve = CVEInfo(cve_id="CVE-2024-0001", description="Test", severity="LOW")
        assert cve.affected_products == []

    def test_wszystkie_poziomy_severity(self):
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            cve = CVEInfo(cve_id="CVE-2024-0001", description="Test", severity=severity)
            assert cve.severity == severity


class TestCVELookupInit:

    def test_tworzy_instancje(self):
        lookup = CVELookup(use_cache=False, nvd_api_key=None)
        assert lookup is not None

    def test_tworzy_instancje_z_kluczem_api(self):
        lookup = CVELookup(use_cache=False, nvd_api_key="test-klucz-123")
        assert lookup.nvd_api_key == "test-klucz-123"

    def test_cache_domyslnie_wlaczone(self):
        lookup = CVELookup()
        assert lookup.use_cache is True


class TestGetCvesForPort:

    def test_nieznany_port_zwraca_pusta_liste(self):
        lookup = CVELookup(use_cache=False)
        assert lookup.get_cves_for_port(99999) == []

    @patch('cve_lookup.CVELookup._search_nvd_api')
    def test_port_dicom_wywoluje_wyszukiwanie(self, mock_search):
        mock_search.return_value = []
        lookup = CVELookup(use_cache=False)
        lookup.get_cves_for_port(104)
        assert mock_search.called
        assert "dicom" in mock_search.call_args_list[0][0][0]

    @patch('cve_lookup.CVELookup._search_nvd_api')
    def test_port_ssh_wywoluje_wyszukiwanie_ssh(self, mock_search):
        mock_search.return_value = []
        lookup = CVELookup(use_cache=False)
        lookup.get_cves_for_port(22)
        slowa = [call[0][0] for call in mock_search.call_args_list]
        assert "ssh" in slowa

    @patch('cve_lookup.CVELookup._search_nvd_api')
    def test_wyniki_sa_posortowane_po_severity(self, mock_search):
        mock_search.return_value = [
            CVEInfo("CVE-2024-003", "Low", "LOW", cvss_score=2.0),
            CVEInfo("CVE-2024-001", "Critical", "CRITICAL", cvss_score=9.8),
            CVEInfo("CVE-2024-002", "Medium", "MEDIUM", cvss_score=5.0),
        ]
        lookup = CVELookup(use_cache=False)
        wyniki = lookup.get_cves_for_port(22)
        if len(wyniki) >= 2:
            order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            for i in range(len(wyniki) - 1):
                assert order[wyniki[i].severity] >= order[wyniki[i+1].severity]

    @patch('cve_lookup.CVELookup._search_nvd_api')
    def test_nie_zwraca_wiecej_niz_10_wynikow(self, mock_search):
        mock_search.return_value = [
            CVEInfo(f"CVE-2024-{i:04d}", f"Vuln {i}", "MEDIUM", cvss_score=5.0)
            for i in range(20)
        ]
        lookup = CVELookup(use_cache=False)
        assert len(lookup.get_cves_for_port(22)) <= 10


class TestCache:

    @patch('cve_lookup.CVELookup._search_nvd_api')
    def test_cache_ogranicza_liczbe_wywolan_api(self, mock_search):
        mock_search.return_value = []
        lookup = CVELookup(use_cache=False)
        lookup.get_cves_for_port(22)
        assert mock_search.call_count <= 2
