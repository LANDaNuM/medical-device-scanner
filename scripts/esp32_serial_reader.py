#!/usr/bin/env python3
"""
Odbiornik danych z ESP32 podłączonego do Raspberry Pi przez USB (port szeregowy).

Użycie:
  1. Podłącz ESP32 do Pi kablem USB.
  2. Na ESP32 wgraj np. esp32_examples/ESP32_Agent_Serial.ino (wysyła linie JSON z wynikami BLE).
  3. Na Pi: python scripts/esp32_serial_reader.py

Opcjonalnie: --port /dev/ttyUSB0 lub /dev/ttyACM0 (domyślnie auto)
             --out plik.json (zapis linii do pliku)
"""
import argparse
import json
import sys

try:
    import serial
except ImportError:
    print("Zainstaluj: pip install pyserial")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Czytaj dane z ESP32 przez USB (Serial)")
    parser.add_argument("--port", default=None, help="Port, np. /dev/ttyUSB0 lub /dev/ttyACM0")
    parser.add_argument("--baud", type=int, default=115200, help="Prędkość (domyślnie 115200)")
    parser.add_argument("--out", default=None, help="Zapisuj linie do pliku (np. esp32_scan.json)")
    args = parser.parse_args()

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
    try:
        while True:
            line = ser.readline()
            if not line:
                continue
            try:
                s = line.decode("utf-8").strip()
            except UnicodeDecodeError:
                continue
            if not s:
                continue
            print(s)
            if out_file:
                out_file.write(s + "\n")
                out_file.flush()
            try:
                j = json.loads(s)
                if j.get("agent") == "ESP32" and j.get("status") == "ready":
                    print("  -> ESP32 agent gotowy.")
            except json.JSONDecodeError:
                pass
    except KeyboardInterrupt:
        print("\nKoniec.")
    finally:
        ser.close()
        if out_file:
            out_file.close()


if __name__ == "__main__":
    main()
