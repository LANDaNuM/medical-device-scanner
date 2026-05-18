# Medical Device Security Scanner

Open-source tool for security auditing of medical and IoT devices (BLE, WiFi, USB, NFC).

## Purpose

- **Discover** devices on the network (Bluetooth Low Energy, WiFi, USB, NFC)
- **Analyse** security (encryption, pairing, open ports, known vulnerabilities)
- **Detect anomalies** using ML (Isolation Forest, LOF, One-Class SVM)
- **Generate reports** (JSON, PDF, SIEM export) and optional email delivery

## Quick start

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/medical-device-scanner.git
cd medical-device-scanner

# Optional: use a virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run scanner
python src/scanner.py
```

## Supported protocols

| Protocol | Description |
|----------|-------------|
| **BLE** | Bluetooth Low Energy – real devices in range, GATT-based encryption detection. Requires `bleak`. |
| **WiFi** | Local network scan, open ports, DICOM/HL7 hints. Uses Python + optional nmap. |
| **USB** | USB and serial devices attached to the host. Requires `pyusb`, `pyserial`. |
| **NFC** | NFC tags/cards. Requires NFC reader (e.g. ACR122U) and `nfcpy`. |

**Examples:**

```bash
python src/scanner.py --ble              # BLE only
python src/scanner.py --wifi             # WiFi only
python src/scanner.py --ble --wifi       # BLE + WiFi
python src/scanner.py --audit            # Full security audit (vulnerability tests, port scan)
python src/scanner.py --ble --audit --report-email you@example.com  # BLE audit + email report
```

## Main features

- **Security audit (`--audit`)**: vulnerability tests, port scanning, risk scoring
- **Report by email (`--report-email`)**: send combined report via SMTP (e.g. Proton) after scan
- **Scheduled scans**: cron-friendly; optional `--ble-duration` for longer BLE scan (default 20 s)
- **SIEM export**: `siem_export_*.jsonl` in `exports/` for Splunk/ELK
- **Web API and dashboard**: `--api` for Flask API + browser UI; Streamlit dashboard in `src/dashboard.py`
- **ESP32 support**: serial reader script for ESP32 agents; see `scripts/esp32_serial_reader.py`

## Requirements

- Python 3.9+
- Optional: Bluetooth adapter (BLE), nmap (WiFi), NFC reader (NFC)

See `requirements.txt`. For flags and options, run `python src/scanner.py --help`.

## Project structure (short)

- `src/scanner.py` – main entry point
- `src/real_scanner.py` – BLE/WiFi/USB/NFC scanners
- `src/vulnerability_tester.py` – audit and port checks
- `scripts/` – ESP32 reader, setup and test scripts
- `exports/` – generated reports (gitignored)
## Testy
pytest tests/ -v

## License

See [LICENSE](LICENSE) if present. Otherwise use and modify at your own responsibility.

## Contributing

Open an issue or pull request on GitHub. For a quick flag reference, run `python src/scanner.py --help`.
