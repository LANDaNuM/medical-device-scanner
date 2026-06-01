#!/usr/bin/env python3
"""
Splunk HEC Forwarder - sends medical device scanner reports to Splunk.
Supports real-time event forwarding and batch report uploads.
"""

import json
import requests
import time
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load .env from project root
project_dir = Path(__file__).parent.parent
load_dotenv(project_dir / ".env")

SPLUNK_HOST: Optional[str] = os.getenv("SPLUNK_HOST")
SPLUNK_TOKEN: Optional[str] = os.getenv("SPLUNK_HEC_TOKEN")
SPLUNK_PORT: str = os.getenv("SPLUNK_HEC_PORT", "8088")
SPLUNK_INDEX: str = os.getenv("SPLUNK_INDEX", "medical_devices")


class SplunkForwarder:
    """Forward events and reports to Splunk HEC (HTTP Event Collector)."""

    def __init__(self) -> None:
        """Initialize Splunk HEC forwarder."""
        if not SPLUNK_HOST or not SPLUNK_TOKEN:
            print("⚠️  Missing SPLUNK_HOST or SPLUNK_HEC_TOKEN in .env")
            sys.exit(1)

        self.url: str = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/collector/event"
        self.headers: Dict[str, str] = {
            "Authorization": f"Splunk {SPLUNK_TOKEN}",
            "Content-Type": "application/json"
        }
        print(f"🔗 Splunk HEC: {self.url}")
        print(f"📦 Index: {SPLUNK_INDEX}")

    def send_event(self, data: Dict[str, Any], source: str = "medical_scanner") -> bool:
        """
        Send a single event to Splunk.
        
        Args:
            data: Event data dictionary
            source: Event source identifier
            
        Returns:
            True if successful, False otherwise
        """
        payload: Dict[str, Any] = {
            "time": time.time(),
            "host": "medical-device-scanner",
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
                print(f"⚠️  HEC error {r.status_code}: {r.text}")
                return False
        except requests.exceptions.Timeout:
            print(f"⚠️  Timeout connecting to Splunk")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"⚠️  Connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending event: {type(e).__name__}: {e}")
            return False

    def send_report(self, report_path: str) -> bool:
        """
        Send a report JSON file to Splunk.
        
        Supports format: {"report_timestamp": ..., "scan": {"devices": [...]}, ...}
        
        Args:
            report_path: Path to report JSON file
            
        Returns:
            True if successful, False otherwise
        """
        path = Path(report_path)
        if not path.exists():
            print(f"⚠️  Report file not found: {path}")
            return False

        print(f"\n📄 Loading: {path.name}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in report: {e}")
            return False
        except IOError as e:
            print(f"❌ Cannot read report file: {e}")
            return False

        # Main format: dict with 'scan' key
        if isinstance(data, dict) and 'scan' in data:
            devices = data['scan'].get('devices', [])
            report_ts = data.get('report_timestamp', '')
            total = data['scan'].get('total_devices', len(devices))

            print(f"🕐 Report timestamp: {report_ts}")
            print(f"📊 Devices: {total}")

            # Send summary event
            summary_event: Dict[str, Any] = {
                "event_type": "scan_summary",
                "report_timestamp": report_ts,
                "total_devices": total,
                "scan_duration": data['scan'].get('scan_duration', 'unknown')
            }
            self.send_event(summary_event, source="medical_scanner:summary")

            # Send each device individually
            success_count = 0
            for i, device in enumerate(devices, 1):
                if self.send_event(device, source="medical_scanner:device"):
                    success_count += 1
                if i % 10 == 0:
                    print(f"  ✓ Sent {i}/{total} devices")

            print(f"✅ Sent {success_count}/{total} devices to Splunk")
            return success_count > 0

        else:
            print("❌ Invalid report format")
            return False

    def send_all_reports(self, reports_dir: str) -> None:
        """
        Send all reports from a directory to Splunk.
        
        Args:
            reports_dir: Directory containing report files
        """
        reports_path = Path(reports_dir)
        reports = sorted(reports_path.glob("combined_report_*.json"))

        if not reports:
            print(f"⚠️  No reports found in: {reports_path}")
            return

        print(f"📁 Found {len(reports)} reports")
        for report in reports:
            try:
                self.send_report(str(report))
                time.sleep(0.5)  # Brief delay between reports
            except Exception as e:
                print(f"❌ Error sending report {report.name}: {type(e).__name__}: {e}")


if __name__ == "__main__":
    forwarder = SplunkForwarder()

    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Mode: send all reports from directory
        if arg == "--all":
            reports_dir = sys.argv[2] if len(sys.argv) > 2 else "reports"
            forwarder.send_all_reports(reports_dir)

        # Mode: send specific file
        else:
            forwarder.send_report(arg)

    else:
        # Default: send latest report from reports/
        reports = sorted(
            Path(project_dir / "reports").glob("combined_report_*.json")
        )
        if not reports:
            print("⚠️  No reports found in reports/ directory")
            sys.exit(1)

        latest = reports[-1]
        print(f"📄 No argument provided – using latest report: {latest.name}")
        forwarder.send_report(str(latest))
