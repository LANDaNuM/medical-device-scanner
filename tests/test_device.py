"""
Testy jednostkowe dla device.py
Uruchomienie: pytest tests/test_device.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest
from device import Device, DeviceType, Protocol


# ============================================================
# POMOCNICZE FUNKCJE - tworzą gotowe urządzenia do testów
# ============================================================

def make_device(has_encryption=True, requires_pairing=True, name="GlucoSmart Pro"):
    """Tworzy przykładowe urządzenie BLE do testów."""
    return Device(
        mac_address="AA:BB:CC:DD:EE:01",
        name=name,
        device_type=DeviceType.GLUCOSE_METER,
        protocol=Protocol.BLE,
        has_encryption=has_encryption,
        requires_pairing=requires_pairing,
    )


# ============================================================
# TESTY: calculate_security_score()
# ============================================================

class TestCalculateSecurityScore:

    def test_urzadzenie_bezpieczne_ma_wysoki_wynik(self):
        """Urządzenie z szyfrowaniem i parowaniem powinno mieć wynik 100."""
        device = make_device(has_encryption=True, requires_pairing=True)
        wynik = device.calculate_security_score()
        assert wynik == 100

    def test_brak_szyfrowania_obniza_wynik_o_30(self):
        """Brak szyfrowania odejmuje 30 punktów."""
        device = make_device(has_encryption=False, requires_pairing=True)
        wynik = device.calculate_security_score()
        assert wynik == 70

    def test_brak_parowania_obniza_wynik_o_20(self):
        """Brak parowania odejmuje 20 punktów."""
        device = make_device(has_encryption=True, requires_pairing=False)
        wynik = device.calculate_security_score()
        assert wynik == 80

    def test_brak_wszystkiego_obniza_wynik_o_50(self):
        """Brak szyfrowania i parowania odejmuje 50 punktów."""
        device = make_device(has_encryption=False, requires_pairing=False)
        wynik = device.calculate_security_score()
        assert wynik == 50

    def test_wynik_nie_spada_ponizej_zera(self):
        """Wynik nigdy nie powinien być ujemny, nawet z wieloma podatnościami."""
        device = make_device(has_encryption=False, requires_pairing=False)
        # Dodajemy 10 podatności - każda -25 pkt, razem -250
        for i in range(10):
            device.vulnerabilities.append(f"CVE-2024-{i:04d}")
        wynik = device.calculate_security_score()
        assert wynik == 0

    def test_jedna_podatnosc_obniza_wynik_o_25(self):
        """Jedna podatność odejmuje 25 punktów."""
        device = make_device(has_encryption=True, requires_pairing=True)
        device.vulnerabilities.append("CVE-2024-0001")
        wynik = device.calculate_security_score()
        assert wynik == 75


# ============================================================
# TESTY: add_vulnerability()
# ============================================================

class TestAddVulnerability:

    def test_dodaje_nowa_podatnosc(self):
        """Nowa podatność powinna zostać dodana do listy."""
        device = make_device()
        device.add_vulnerability("CVE-2024-0001")
        assert "CVE-2024-0001" in device.vulnerabilities

    def test_nie_dodaje_duplikatu(self):
        """Ta sama podatność nie powinna być dodana dwa razy."""
        device = make_device()
        device.add_vulnerability("CVE-2024-0001")
        device.add_vulnerability("CVE-2024-0001")
        assert device.vulnerabilities.count("CVE-2024-0001") == 1

    def test_dodanie_podatnosci_aktualizuje_wynik(self):
        """Po dodaniu podatności wynik bezpieczeństwa powinien się zaktualizować."""
        device = make_device(has_encryption=True, requires_pairing=True)
        assert device.calculate_security_score() == 100
        device.add_vulnerability("CVE-2024-0001")
        assert device.security_score == 75

    def test_mozna_dodac_wiele_roznych_podatnosci(self):
        """Kilka różnych podatności powinno być dodanych bez problemów."""
        device = make_device()
        device.add_vulnerability("CVE-2024-0001")
        device.add_vulnerability("CVE-2024-0002")
        device.add_vulnerability("CVE-2024-0003")
        assert len(device.vulnerabilities) == 3


# ============================================================
# TESTY: get_device_fingerprint()
# ============================================================

class TestGetDeviceFingerprint:

    def test_fingerprint_zawiera_protokol(self):
        """Fingerprint powinien zawierać protokół urządzenia."""
        device = make_device()
        fingerprint = device.get_device_fingerprint()
        assert "BLE" in fingerprint

    def test_fingerprint_zawiera_typ_urzadzenia(self):
        """Fingerprint powinien zawierać typ urządzenia."""
        device = make_device()
        fingerprint = device.get_device_fingerprint()
        assert "glucose_meter" in fingerprint

    def test_fingerprint_zawiera_skrot_mac(self):
        """Fingerprint powinien zawierać ostatnie 6 znaków adresu MAC."""
        device = make_device()
        # MAC: AA:BB:CC:DD:EE:01 → ostatnie 6 to DDEE01
        fingerprint = device.get_device_fingerprint()
        assert "DDEE01" in fingerprint

    def test_fingerprint_zawiera_producenta_i_model(self):
        """Fingerprint powinien zawierać producenta i model jeśli są dostępne."""
        device = make_device()
        device.manufacturer = "MedTech"
        device.model = "GT-100"
        fingerprint = device.get_device_fingerprint()
        assert "MedTech" in fingerprint
        assert "GT-100" in fingerprint


# ============================================================
# TESTY: get_display_name()
# ============================================================

class TestGetDisplayName:

    def test_zwraca_nazwe_urzadzenia(self):
        """Jeśli urządzenie ma nazwę, powinna być zwrócona."""
        device = make_device(name="GlucoSmart Pro")
        assert device.get_display_name() == "GlucoSmart Pro"

    def test_fallback_do_producenta_i_modelu(self):
        """Jeśli brak nazwy, użyj producenta + modelu."""
        device = make_device(name="Unknown")
        device.manufacturer = "Philips"
        device.model = "IntelliVue"
        assert device.get_display_name() == "Philips IntelliVue"

    def test_fallback_do_protokolu_i_mac(self):
        """Jeśli brak nazwy, producenta i modelu, użyj protokołu + MAC."""
        device = Device(
            mac_address="AA:BB:CC:DD:EE:FF",
            name="Unknown",
            device_type=DeviceType.UNKNOWN,
            protocol=Protocol.BLE,
        )
        nazwa = device.get_display_name()
        # Powinno zawierać protokół i fragment MAC
        assert "BLE" in nazwa
        assert "EEFF" in nazwa.upper() or "DDEE" in nazwa.upper() or "FF" in nazwa.upper()


# ============================================================
# TESTY: to_dict()
# ============================================================

class TestToDict:

    def test_zwraca_slownik(self):
        """to_dict() powinno zwrócić słownik."""
        device = make_device()
        result = device.to_dict()
        assert isinstance(result, dict)

    def test_zawiera_wymagane_pola(self):
        """Słownik powinien zawierać kluczowe pola."""
        device = make_device()
        result = device.to_dict()
        for pole in ["mac_address", "protocol", "has_encryption", "security_score"]:
            assert pole in result, f"Brakuje pola: {pole}"

    def test_has_encryption_jest_bool(self):
        """has_encryption w słowniku powinno być bool (nie numpy bool)."""
        device = make_device(has_encryption=True)
        result = device.to_dict()
        assert isinstance(result["has_encryption"], bool)

    def test_puste_pola_sa_usuniete(self):
        """Pola None, puste stringi i puste listy powinny być usunięte."""
        device = Device(
            mac_address="AA:BB:CC:DD:EE:01",
            name="Test",
            device_type=DeviceType.UNKNOWN,
            protocol=Protocol.BLE,
        )
        result = device.to_dict()
        # manufacturer jest None - nie powinno być w słowniku
        assert "manufacturer" not in result
