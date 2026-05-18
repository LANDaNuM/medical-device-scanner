#!/usr/bin/env python3
"""
Splunk HEC Forwarder - wysyła raporty skanera urządzeń medycznych do Splunka
"""

import json
import requests
import time
import os
import sys
from pathlib import Path
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Załaduj .env z katalogu głównego projektu
project_dir = Path(__file__).parent.parent
load_dotenv(project_dir / ".env")

SPLUNK_HOST  = os.getenv("SPLUNK_HOST")
SPLUNK_TOKEN = os.getenv("SPLUNK_HEC_TOKEN")
SPLUNK_PORT  = os.getenv("SPLUNK_HEC_PORT", "8088")
SPLUNK_INDEX = os.getenv("SPLUNK_INDEX", "medical_devices")


class SplunkForwarder:

    def __init__(self):
        if not SPLUNK_HOST or not SPLUNK_TOKEN:
            print("⚠️  Brak SPLUNK_HOST lub SPLUNK_HEC_TOKEN w pliku .env")
            sys.exit(1)

        self.url = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/collector/event"
        self.headers = {
            "Authorization": f"Splunk {SPLUNK_TOKEN}",
            "Content-Type": "application/json"
        }
        print(f"🔗 Splunk HEC: {self.url}")
        print(f"📦 Index: {SPLUNK_INDEX}")

    def send_event(self, data: dict, source: str = "medical_scanner") -> bool:
        """Wysyła pojedyncze zdarzenie do Splunka przez HEC."""
        payload = {
            "time": time.time(),
            "host": "raspberry-pi",
            "source": source,
            "sourcetype": "_json",
            "index": SPLUNK_INDEX,
            "event": data
        }
        try:
            r = requests.post(
                self.url,
                headers=self.headers,
                json=payload,
                verify=False,
                timeout=10
            )
            if r.status_code == 200:
                return True
            else:
                print(f"⚠️  HEC błąd {r.status_code}: {r.text}")
                return False
        except Exception as e:
            print(f"⚠️  Błąd połączenia: {e}")
            return False

    def send_report(self, report_path) -> bool:
        """
        Wysyła raport JSON do Splunka.
        Obsługuje format: {"report_timestamp": ..., "scan": {"devices": [...]}, ...}
        """
        path = Path(report_path)
        if not path.exists():
            print(f"⚠️  Plik nie istnieje: {path}")
            return False

        print(f"\n📄 Wczytuję: {path.name}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # --- Format główny: dict z kluczem 'scan' ---
        if isinstance(data, dict) and 'scan' in data:
            devices = data['scan'].get('devices', [])
            report_ts = data.get('report_timestamp', '')
            total = data['scan'].get('total_devices', len(devices))

            print(f"🕐 Timestamp raportu: {report_ts}")
            print(f"📡 Urządzeń w raporcie: {total}")

            # Wyślij podsumowanie raportu jako osobny event
            meta = {
                'event_type': 'scan_summary',
                'report_timestamp': report_ts,
                'total_devices': total,
                'protocols_scanned': data['scan'].get('protocols_scanned', []),
                'report_file': path.name,
            }
            if 'threat_intelligence_summary' in data:
                meta['threat_intelligence_summary'] = data['threat_intelligence_summary']
            if 'analysis' in data:
                meta['analysis'] = data['analysis']

            self.send_event(meta, source="scanner_meta")
            print(f"✅ Wysłano podsumowanie skanu")

            # Wyślij każde urządzenie jako osobny event
            print(f"📤 Wysyłam urządzenia...")
            ok = 0
            for i, device in enumerate(devices, 1):
                enriched = dict(device)
                enriched['event_type'] = 'device'
                enriched['report_timestamp'] = report_ts
                enriched['report_file'] = path.name
                if self.send_event(enriched):
                    ok += 1
                    # Pokaż postęp co 10 urządzeń
                    if i % 10 == 0 or i == len(devices):
                        print(f"   {i}/{len(devices)} urządzeń...", end='\r')

            print(f"\n✅ Wysłano {ok}/{len(devices)} urządzeń do Splunka")
            return ok == len(devices)

        # --- Format alternatywny: lista urządzeń ---
        elif isinstance(data, list):
            print(f"📤 Wysyłam {len(data)} eventów...")
            ok = 0
            for item in data:
                if self.send_event(item):
                    ok += 1
            print(f"✅ {ok}/{len(data)} wysłanych")
            return ok == len(data)

        # --- Pojedynczy obiekt ---
        else:
            print("📤 Wysyłam jako pojedynczy event...")
            result = self.send_event(data)
            if result:
                print("✅ Wysłano")
            return result

    def send_all_reports(self, reports_dir: str) -> None:
        """Wysyła wszystkie raporty z katalogu."""
        reports_path = Path(reports_dir)
        reports = sorted(reports_path.glob("combined_report_*.json"))

        if not reports:
            print(f"⚠️  Brak raportów w: {reports_path}")
            return

        print(f"📁 Znaleziono {len(reports)} raportów")
        for report in reports:
            self.send_report(report)
            time.sleep(0.5)  # krótka przerwa między raportami


# ─── Uruchomienie ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    forwarder = SplunkForwarder()

    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Tryb: wyślij wszystkie raporty z katalogu
        if arg == "--all":
            reports_dir = sys.argv[2] if len(sys.argv) > 2 else "reports"
            forwarder.send_all_reports(reports_dir)

        # Tryb: wyślij konkretny plik
        else:
            forwarder.send_report(arg)

    else:
        # Domyślnie: ostatni raport z katalogu reports/
        reports = sorted(
            Path(project_dir / "reports").glob("combined_report_*.json")
        )
        if not reports:
            print("⚠️  Brak raportów w katalogu reports/")
            sys.exit(1)

        latest = reports[-1]
        print(f"📄 Brak argumentu — używam ostatniego raportu: {latest.name}")
        forwarder.send_report(latest)
