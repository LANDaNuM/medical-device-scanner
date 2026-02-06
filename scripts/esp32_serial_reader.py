#!/usr/bin/env python3
"""
Odbiornik danych z ESP32 podłączonego do Raspberry Pi przez USB (port szeregowy).

Użycie:
  1. Podłącz ESP32 do Pi kablem USB.
  2. Na ESP32 wgraj esp32_examples/ESP32_Unified_Scanner (BLE + WiFi, tylko zmiany).
  3. Na Pi: python scripts/esp32_serial_reader.py --out wyniki_esp32.json --enrich

Opcje: --port, --baud, --out, --enrich
       --duration N       skanuj N sekund i zakończ (raport w --out); do cron/at
       --report-email ADR po zakończeniu (np. z --duration) wyślij raport emailem (SMTP z .env)
       --on-new-scan      przy event new (BLE) uruchom skaner: python src/scanner.py --ble (co najwyżej co 60 s)
       --alert-email ADR  wyślij mail przy nowym urządzeniu (SMTP z .env)
       --alert-slack URL  wyślij POST do Slack webhook przy nowym urządzeniu
       --alert-splunk PLIK dopisz linię do pliku (Splunk monitoruje ten plik)
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
    print("Zainstaluj: pip install pyserial")
    sys.exit(1)

# Katalog projektu (nad scripts/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Znane BLE Service UUID (medyczne / typowe) – do podpowiedzi typu urządzenia
BLE_SERVICE_HINTS = {
    "00001808": "glukometr",
    "0000180d": "puls/tętno",
    "00001810": "ciśnienie",
    "0000180f": "bateria",
    "0000180a": "informacje_o_urządzeniu",
    "00001800": "gatt_generic",
    "0000fd6f": "fast_pair",
    "0000fe95": "xiaomi",
}


def _enrich_ble(oui_lookup, j):
    """Dodaje vendor (OUI), device_type_hint, vulnerability_hints do rekordu BLE."""
    if j.get("type") != "ble":
        return j
    out = dict(j)
    mac = j.get("mac") or ""
    name = j.get("name") or ""
    service_uuid = (j.get("service_uuid") or "").lower().replace("-", "")[:8]

    # Producent z OUI (pierwsze 3 bajty MAC)
    try:
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        vendor = oui_lookup.lookup(mac)
        if vendor:
            out["vendor"] = vendor
    except Exception:
        pass

    # Typ urządzenia z UUID usługi
    if service_uuid and service_uuid in BLE_SERVICE_HINTS:
        out["device_type_hint"] = BLE_SERVICE_HINTS[service_uuid]

    # Podpowiedzi podatności (tylko sensowne – bez „brak_nazwy”)
    hints = []
    if j.get("ble_no_auth") is True:
        hints.append("ble_bez_parowania")
    if service_uuid in ("00001808", "0000180d", "00001810"):
        hints.append("możliwe_urządzenie_medyczne")
    if hints:
        out["vulnerability_hints"] = hints

    return out


def _trigger_scan(project_root, debounce_sec=60):
    """Uruchamia skaner BLE na Pi (co najwyżej co debounce_sec)."""
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
        print("  [on-new-scan] Uruchomiono skaner BLE w tle.", file=sys.stderr)
    except Exception:
        pass


def _alert_email(addr, body_subject, env):
    """Wysyła maila (SMTP z .env)."""
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
    msg["Subject"] = f"[ESP32] Nowe urządzenie: {body_subject[:80]}"
    msg["From"] = from_addr
    msg["To"] = addr
    msg.attach(MIMEText(body_subject, "plain", "utf-8"))
    try:
        with smtplib.SMTP(smtp, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(from_addr, addr, msg.as_string())
        print("  [alert] Email wysłany.", file=sys.stderr)
    except Exception:
        pass


def _alert_slack(webhook_url, body):
    """Wysyła POST do Slack Incoming Webhook."""
    try:
        import urllib.request
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps({"text": body}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
        print("  [alert] Slack wysłany.", file=sys.stderr)
    except Exception:
        pass


def _alert_splunk(filepath, line):
    """Dopisywanie linii do pliku (Splunk monitoruje ten plik)."""
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print("  [alert] Dopisano do Splunk pliku.", file=sys.stderr)
    except Exception:
        pass


def _send_report_email(addr, filepath, env):
    """Wysyła raport (zawartość pliku) emailem po zakończeniu skanowania (--duration)."""
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
        print("  [report] Brak SMTP_SERVER/SMTP_USER/SMTP_PASSWORD lub adresu. Sprawdź .env", file=sys.stderr)
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            body = f.read()
    except Exception as e:
        print(f"  [report] Nie można odczytać pliku raportu: {e}", file=sys.stderr)
        return
    msg = MIMEMultipart()
    msg["Subject"] = f"[ESP32] Raport skanowania {os.path.basename(filepath)}"
    msg["From"] = from_addr
    msg["To"] = addr
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        with smtplib.SMTP(smtp, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(from_addr, addr, msg.as_string())
        print("  [report] Raport wysłany emailem.", file=sys.stderr)
    except Exception as e:
        print(f"  [report] Błąd SMTP (sprawdź .env, token Proton, sieć): {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Czytaj dane z ESP32 przez USB (Serial)")
    parser.add_argument("--port", default=None, help="Port, np. /dev/ttyUSB0 lub /dev/ttyACM0")
    parser.add_argument("--baud", type=int, default=115200, help="Prędkość (domyślnie 115200)")
    parser.add_argument("--out", default=None, help="Zapisuj linie do pliku (np. esp32_scan.json)")
    parser.add_argument("--duration", type=int, default=None, metavar="N", help="Skanuj N sekund i zakończ (raport w --out); do cron/at")
    parser.add_argument("--report-email", metavar="ADR", default=None, help="Po zakończeniu (np. z --duration) wyślij raport emailem (SMTP z .env)")
    parser.add_argument("--enrich", action="store_true", help="Dodaj OUI (producent), typ urządzenia, podpowiedzi podatności")
    parser.add_argument("--on-new-scan", action="store_true", help="Przy event new (BLE) uruchom skaner --ble (co najwyżej co 60 s)")
    parser.add_argument("--alert-email", metavar="ADR", default=None, help="Wyślij email przy nowym urządzeniu (SMTP z .env)")
    parser.add_argument("--alert-slack", metavar="URL", default=None, help="Wyślij do Slack webhook przy nowym urządzeniu")
    parser.add_argument("--alert-splunk", metavar="PLIK", default=None, help="Dopisz linię do pliku przy nowym urządzeniu (Splunk)")
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
            print("Wzbogacanie włączone (OUI, typ urządzenia, podpowiedzi podatności).")
        except Exception as e:
            print(f"Uwaga: --enrich niedostępne ({e}). Wyświetlam surowe linie.", file=sys.stderr)
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
        print("Nie znaleziono portu. Podaj ręcznie: --port /dev/ttyUSB0")
        sys.exit(1)

    print(f"Łączę z {port} @ {args.baud}...")
    try:
        ser = serial.Serial(port, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"Błąd portu: {e}")
        sys.exit(1)

    out_file = open(args.out, "w") if args.out else None
    start_time = time.time()
    duration_reached = False
    try:
        while True:
            if args.duration is not None and (time.time() - start_time) >= args.duration:
                duration_reached = True
                print(f"\n[OK] Koniec skanowania po {args.duration} s. Raport: {args.out or '(stdout)'}", file=sys.stderr)
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
                    print("  -> ESP32 agent gotowy (tryb: tylko zmiany).")
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
                    body = f"Nowe urządzenie: type={j.get('type')} mac={j.get('mac','')} name={j.get('name','')} ssid={j.get('ssid','')}"
                    if args.alert_email:
                        _alert_email(args.alert_email, body, env)
                    if args.alert_slack:
                        _alert_slack(args.alert_slack, body)
                    if args.alert_splunk:
                        _alert_splunk(args.alert_splunk, s)
                if args.enrich and oui_lookup and j.get("type") == "ble":
                    enriched = _enrich_ble(oui_lookup, j)
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
