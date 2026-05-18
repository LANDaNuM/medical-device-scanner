#!/usr/bin/env python3
"""
Read data from ESP32 connected to Raspberry Pi via USB (serial port).

Usage:
  1. Connect ESP32 to Pi with USB cable.
  2. Flash esp32_examples/ESP32_Unified_Scanner (BLE + WiFi, changes only) on ESP32.
  3. On Pi: python scripts/esp32_serial_reader.py --out wyniki_esp32.json --enrich

Options: --port, --baud, --out, --enrich
         --duration N       scan for N seconds then exit (report in --out); for cron/at
         --report-email ADR after finish (e.g. with --duration) send report by email (SMTP from .env)
         --on-new-scan      on event new (BLE) run scanner: python src/scanner.py --ble (at most every 60 s)
         --alert-email ADR  send email on new device (SMTP from .env)
         --alert-slack URL  POST to Slack webhook on new device
         --alert-splunk FILE append line to file (Splunk monitors this file)
"""
import argparse
import json
import os
import subprocess
import sys
import time

try:
    import serial
except ImportError:
    print("Install: pip install pyserial")
    sys.exit(1)

# Project root (parent of scripts/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Known BLE service UUIDs (medical / common) – device type hints
BLE_SERVICE_HINTS = {
    "00001808": "glucose_meter",
    "0000180d": "heart_rate",
    "00001810": "blood_pressure",
    "0000180f": "battery",
    "0000180a": "device_info",
    "00001800": "gatt_generic",
    "0000fd6f": "fast_pair",
    "0000fe95": "xiaomi",
}

# BLE manufacturer_data prefixes (first 2 bytes = Company ID, hex) – manufacturer hint
BLE_MANUFACTURER_HINTS = {
    "4c00": "Apple (e.g. AirTag, AirPods, Find My)",
    "5900": "Google",
    "6d00": "Microsoft",
    "e000": "Garmin",
    "7500": "Samsung (some devices)",
    "fe95": "Xiaomi (Mi)",
    "fd6f": "Fast Pair",
}


def _enrich_ble(oui_lookup, j):
    """Add vendor (OUI), device_type_hint, vulnerability_hints to BLE record."""
    if j.get("type") != "ble":
        return j
    out = dict(j)
    mac = j.get("mac") or ""
    name = j.get("name") or ""
    service_uuid = (j.get("service_uuid") or "").lower().replace("-", "")[:8]

    # Vendor from OUI (first 3 bytes of MAC)
    try:
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        vendor = oui_lookup.lookup(mac)
        if vendor:
            out["vendor"] = vendor
    except Exception:
        pass

    # Device type from service UUID
    if service_uuid and service_uuid in BLE_SERVICE_HINTS:
        out["device_type_hint"] = BLE_SERVICE_HINTS[service_uuid]

    # Manufacturer from manufacturer_data (2-byte prefix = Company ID)
    mfg = (j.get("manufacturer_data") or "").lower().replace(" ", "")[:4]
    if mfg in BLE_MANUFACTURER_HINTS:
        out["manufacturer_hint"] = BLE_MANUFACTURER_HINTS[mfg]

    # Vulnerability hints (meaningful only)
    hints = []
    if j.get("ble_no_auth") is True:
        hints.append("ble_no_pairing")
    if service_uuid in ("00001808", "0000180d", "00001810"):
        hints.append("possible_medical_device")
    if hints:
        out["vulnerability_hints"] = hints

    return out


def _enrich_wifi(oui_lookup, j):
    """Add vendor (OUI) for WiFi AP when bssid (AP MAC) is present."""
    if j.get("type") != "wifi":
        return j
    bssid = j.get("bssid") or j.get("mac") or ""
    if not bssid:
        return j
    out = dict(j)
    try:
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        vendor = oui_lookup.lookup(bssid)
        if vendor:
            out["ap_vendor"] = vendor
    except Exception:
        pass
    return out


def _trigger_scan(project_root, debounce_sec=60):
    """Run BLE scanner on Pi (at most every debounce_sec)."""
    now = time.time()
    if not hasattr(_trigger_scan, "last"):
        _trigger_scan.last = 0.0
    if now - _trigger_scan.last < debounce_sec:
        return
    _trigger_scan.last = now
    scanner = os.path.join(project_root, "src", "scanner.py")
    if not os.path.isfile(scanner):
        return
    try:
        subprocess.Popen(
            [sys.executable, scanner, "--ble"],
            cwd=project_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("  [on-new-scan] Started BLE scanner in background.", file=sys.stderr)
    except Exception:
        pass


def _alert_email(addr, body_subject, env):
    """Send email (SMTP from .env)."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
    except ImportError:
        return
    smtp = env.get("SMTP_SERVER") or env.get("SMTP_HOST")
    port = int(env.get("SMTP_PORT", 587))
    user = env.get("SMTP_USER")
    password = env.get("SMTP_PASSWORD")
    from_addr = env.get("EMAIL_FROM") or user
    if not smtp or not user or not password or not addr:
        return
    msg = MIMEMultipart()
    msg["Subject"] = f"[ESP32] New device: {body_subject[:80]}"
    msg["From"] = from_addr
    msg["To"] = addr
    msg.attach(MIMEText(body_subject, "plain", "utf-8"))
    try:
        with smtplib.SMTP(smtp, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(from_addr, addr, msg.as_string())
        print("  [alert] Email sent.", file=sys.stderr)
    except Exception:
        pass


def _alert_slack(webhook_url, body):
    """Send POST to Slack Incoming Webhook."""
    try:
        import urllib.request
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps({"text": body}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
        print("  [alert] Slack sent.", file=sys.stderr)
    except Exception:
        pass


def _alert_splunk(filepath, line):
    """Append line to file (Splunk monitors this file)."""
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print("  [alert] Appended to Splunk file.", file=sys.stderr)
    except Exception:
        pass


def _send_report_email(addr, filepath, env):
    """Send report (file contents) by email after scan ends (--duration)."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
    except ImportError:
        return
    smtp = env.get("SMTP_SERVER") or env.get("SMTP_HOST")
    port = int(env.get("SMTP_PORT", 587))
    user = env.get("SMTP_USER")
    password = env.get("SMTP_PASSWORD")
    from_addr = env.get("EMAIL_FROM") or user
    if not smtp or not user or not password or not addr:
        print("  [report] Missing SMTP_SERVER/SMTP_USER/SMTP_PASSWORD or address. Check .env", file=sys.stderr)
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            body = f.read()
    except Exception as e:
        print(f"  [report] Cannot read report file: {e}", file=sys.stderr)
        return
    if not body or not body.strip():
        body = "(Report empty – no ESP32 data in this run. Check: ESP32 connected via USB to Pi, port e.g. /dev/ttyUSB0, longer --duration.)"
        print("  [report] Report file empty – sending email with notice.", file=sys.stderr)
    msg = MIMEMultipart()
    msg["Subject"] = f"[ESP32] Scan report {os.path.basename(filepath)}"
    msg["From"] = from_addr
    msg["To"] = addr
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        with smtplib.SMTP(smtp, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(from_addr, addr, msg.as_string())
        print("  [report] Report sent by email.", file=sys.stderr)
    except Exception as e:
        print(f"  [report] SMTP error (check .env, Proton token, network): {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Read data from ESP32 via USB (serial)")
    parser.add_argument("--port", default=None, help="Port, e.g. /dev/ttyUSB0 or /dev/ttyACM0")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default 115200)")
    parser.add_argument("--out", default=None, help="Write lines to file (e.g. esp32_scan.json)")
    parser.add_argument("--duration", type=int, default=None, metavar="N", help="Scan N seconds then exit (report in --out); for cron/at")
    parser.add_argument("--report-email", metavar="ADR", default=None, help="After finish (e.g. with --duration) send report by email (SMTP from .env)")
    parser.add_argument("--enrich", action="store_true", help="Add OUI (vendor), device type, vulnerability hints")
    parser.add_argument("--on-new-scan", action="store_true", help="On event new (BLE) run scanner --ble (at most every 60 s)")
    parser.add_argument("--alert-email", metavar="ADR", default=None, help="Send email on new device (SMTP from .env)")
    parser.add_argument("--alert-slack", metavar="URL", default=None, help="POST to Slack webhook on new device")
    parser.add_argument("--alert-splunk", metavar="FILE", default=None, help="Append line to file on new device (Splunk)")
    args = parser.parse_args()

    env = {}
    env_file = os.path.join(PROJECT_ROOT, ".env")
    if os.path.isfile(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip("'\"").strip()

    oui_lookup = None
    if args.enrich:
        try:
            if PROJECT_ROOT not in sys.path:
                sys.path.insert(0, PROJECT_ROOT)
            from src.oui_lookup import get_oui_lookup
            oui_lookup = get_oui_lookup()
            print("Enrichment on (OUI, device type, vulnerability hints).")
        except Exception as e:
            print(f"Note: --enrich not available ({e}). Showing raw lines.", file=sys.stderr)
            oui_lookup = None

    port = args.port
    if not port:
        import glob
        for p in ["/dev/ttyUSB0", "/dev/ttyACM0", "/dev/serial0"]:
            try:
                ser = serial.Serial(p, args.baud, timeout=0.5)
                ser.close()
                port = p
                break
            except (serial.SerialException, OSError):
                pass
        if not port:
            for p in glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"):
                port = p
                break
    if not port:
        print("No port found. Specify manually: --port /dev/ttyUSB0")
        sys.exit(1)

    print(f"Connecting to {port} @ {args.baud}...")
    try:
        ser = serial.Serial(port, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"Port error: {e}")
        sys.exit(1)

    out_file = open(args.out, "w") if args.out else None
    start_time = time.time()
    duration_reached = False
    try:
        while True:
            if args.duration is not None and (time.time() - start_time) >= args.duration:
                duration_reached = True
                print(f"\n[OK] Scan finished after {args.duration} s. Report: {args.out or '(stdout)'}", file=sys.stderr)
                break
            line = ser.readline()
            if not line:
                continue
            try:
                s = line.decode("utf-8").strip()
            except UnicodeDecodeError:
                continue
            if not s:
                continue
            try:
                j = json.loads(s)
                if j.get("agent") == "ESP32" and j.get("status") in ("ready", "serial", "changes_only"):
                    print("  -> ESP32 agent ready (mode: changes only).")
                    if out_file:
                        out_file.write(s + "\n")
                        out_file.flush()
                    print(s)
                    continue
                if j.get("type") == "heartbeat":
                    print("  [heartbeat] BLE:", j.get("ble_count", 0), "WiFi:", j.get("wifi_count", 0))
                if j.get("event") == "new" and j.get("type") in ("ble", "wifi"):
                    if j.get("type") == "ble" and args.on_new_scan:
                        _trigger_scan(PROJECT_ROOT)
                    body = f"New device: type={j.get('type')} mac={j.get('mac','')} name={j.get('name','')} ssid={j.get('ssid','')}"
                    if args.alert_email:
                        _alert_email(args.alert_email, body, env)
                    if args.alert_slack:
                        _alert_slack(args.alert_slack, body)
                    if args.alert_splunk:
                        _alert_splunk(args.alert_splunk, s)
                if args.enrich and oui_lookup:
                    if j.get("type") == "ble":
                        enriched = _enrich_ble(oui_lookup, j)
                        s = json.dumps(enriched, ensure_ascii=False)
                    elif j.get("type") == "wifi":
                        enriched = _enrich_wifi(oui_lookup, j)
                        s = json.dumps(enriched, ensure_ascii=False)
            except json.JSONDecodeError:
                pass
            print(s)
            if out_file:
                out_file.write(s + "\n")
                out_file.flush()
    except KeyboardInterrupt:
        print("\nKoniec.")
    finally:
        ser.close()
        if out_file:
            out_file.close()
        if duration_reached and args.report_email and args.out and os.path.isfile(args.out):
            _send_report_email(args.report_email, args.out, env)


if __name__ == "__main__":
    main()
