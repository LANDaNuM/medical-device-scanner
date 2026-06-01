# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

Single Python application: **Medical Device Security Scanner** — CLI tool for auditing medical/IoT devices (BLE, WiFi, USB, NFC). Optional Flask REST API + HTML UI (`src/api_server.py`, port 5000) and Streamlit dashboard (`src/dashboard.py`, port 8501). SQLite history DB is file-based (`history.db`); no external database server.

### System dependencies (VM snapshot, not update script)

These are required on the host but are **not** in the update script:

- `python3.12-venv` — needed to create `venv/` (`python3 -m venv venv`)
- `nmap` — WiFi/port scanning via `python-nmap`

Optional for hardware-specific features: BlueZ/bluetooth (BLE), libusb (USB), libnfc (NFC).

### Python environment

```bash
source venv/bin/activate
```

If `venv/` is missing: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt pytest pytest-cov`

Copy env template when needed: `cp .env.example .env` (all API keys optional).

### Common commands

| Task | Command |
|------|---------|
| Run tests | `pytest tests/ -v` |
| Scanner help | `python src/scanner.py --help` |
| WiFi scan | `python src/scanner.py --wifi` |
| Full audit | `python src/scanner.py --wifi --audit` |
| Setup helper | `bash scripts/setup.sh` |
| Flask API + UI | `python src/api_server.py` (port 5000) |
| Streamlit dashboard | `streamlit run src/dashboard.py` (port 8501) |

There is **no** configured linter (no ruff/flake8/mypy in repo). CI only runs pytest (see `.github/workflows/tests.yml`).

### WiFi E2E test (documented path)

Two terminals:

1. **Test device simulator:** `python scripts/test_scanner.py --wifi` (HTTP server on port 8080)
2. **Scanner:** `python src/scanner.py --wifi --no-threat-intel` (threat-intel calls external APIs; skip for offline dev)

Outputs land in `reports/combined_report_*.json` and `exports/siem_export_*.jsonl`.

### Gotchas

- **TensorFlow startup noise:** set `TF_CPP_MIN_LOG_LEVEL=3` when running CLI/API to suppress GPU/oneDNN logs.
- **WiFi scan scope:** `--wifi` scans the local subnet (ARP + nmap), not just localhost. The test server binds to the host LAN IP (e.g. `172.30.0.2:8080`), not necessarily `127.0.0.1`.
- **Flask API JSON:** HTML by default; use `?format=json` or `Accept: application/json` on `/devices`, `/report`, etc.
- **Rust extension:** optional; Python fallback is used if `rust_scanner/` is not built with maturin.
- **BLE/USB/NFC:** require physical adapters; not available in typical cloud VMs.

### Long-running services (use tmux)

```bash
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s wifi-test-server -c /workspace -- zsh -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t wifi-test-server:0.0 'source venv/bin/activate && python scripts/test_scanner.py --wifi' C-m

tmux -f /exec-daemon/tmux.portal.conf new-session -d -s flask-api -c /workspace -- zsh -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t flask-api:0.0 'source venv/bin/activate && TF_CPP_MIN_LOG_LEVEL=3 python src/api_server.py' C-m
```
