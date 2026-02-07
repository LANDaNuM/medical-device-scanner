# Najbardziej przydatne flagi – zestawienie kompleksowe

Krótki plik z flagami, które dają najwięcej: audyt, SIEM, planowanie, raporty.

---

## 1. Skaner główny (`src/scanner.py`)

### Najpełniejszy audyt (maksymalna dokładność)
```bash
python3 src/scanner.py --ble --wifi --audit
```
| Flaga | Znaczenie |
|-------|-----------|
| `--ble` | Skan BLE |
| `--wifi` | Skan WiFi (sieć) |
| `--audit` | Testy podatności, skan portów, pełna analiza |

Bez `--ble`/`--wifi` skaner wybiera protokoły automatycznie. Można dodać `--usb`, `--nfc`.

### Przegląd wyników (API w przeglądarce)
```bash
python3 src/scanner.py --ble --wifi --api
```
| Flaga | Znaczenie |
|-------|-----------|
| `--api` | Serwer API po skanie (przeglądarka) |
| `--api-port 8080` | Port (domyślnie 5000) |

### Eksport do SIEM (domyślnie włączony)
- Plik: `exports/siem_export_YYYYMMDD_HHMMSS.jsonl`
- Wyłączenie: `--no-siem`
- Threat Intelligence (IP w bazach): domyślnie włączone, wyłączenie: `--no-threat-intel`

### Planowanie skanów (na hoście, bez ESP32)
```bash
python3 src/scanner.py --schedule "daily 09:00"
python3 src/scanner.py --schedule "hourly"
python3 src/scanner.py --schedule "every 30 minutes"
```

### Monitoring w czasie rzeczywistym
```bash
python3 src/scanner.py --monitor --interval 300
```
| Flaga | Znaczenie |
|-------|-----------|
| `--monitor` | Cykliczny skan w pętli |
| `--interval N` | Co N sekund (domyślnie 300) |

### Raport e-mail po skanowaniu (cron, audyt)
Raport (plik `combined_report_*.json`) można wysłać mailem – **ta sama konfiguracja SMTP** co dla ESP32 (`.env`, Proton itd.). Przydatne przy zaplanowanym audycie z crona.
```bash
python3 src/scanner.py --audit --report-email twoj@email.me
```
| Flaga | Znaczenie |
|-------|-----------|
| `--report-email ADR` | Po zakończeniu wyślij raport emailem (SMTP z `.env`, jak ESP32) |

### Inne przydatne
| Flaga | Znaczenie |
|-------|-----------|
| `--no-wifi` | Bez skanowania WiFi (szybciej) |
| `--legacy-reports` | Dodatkowo stare pliki scan_*.json, report_*.json |

---

## 2. ESP32 – czytnik szeregowy (`scripts/esp32_serial_reader.py`)

### Planowane skanowanie (cron) + raport e-mail – najbardziej kompleksowe
```bash
python3 scripts/esp32_serial_reader.py --out raporty/esp32_$(date +%Y%m%d).json --enrich --duration 300 --report-email twoj@email.me
```
| Flaga | Znaczenie |
|-------|-----------|
| `--out PLIK` | Zapis linii JSON (raport) |
| `--enrich` | OUI (producent), typ urządzenia, manufacturer_hint, ap_vendor, podpowiedzi podatności |
| `--duration N` | Skan N sekund, potem zakończenie (do cron/at) |
| `--report-email ADR` | Wyślij raport emailem po zakończeniu (SMTP z `.env`) |

### Podgląd na żywo z wzbogacaniem
```bash
python3 scripts/esp32_serial_reader.py --out wyniki.json --enrich
```

### Alerty przy nowym urządzeniu
| Flaga | Znaczenie |
|-------|-----------|
| `--alert-email ADR` | Email przy event "new" (SMTP z `.env`) |
| `--alert-slack URL` | POST do Slack webhook przy "new" |
| `--alert-splunk PLIK` | Dopisanie linii do pliku (Splunk) |
| `--on-new-scan` | Przy BLE "new" uruchom `scanner.py --ble` (co najwyżej co 60 s) |

### Port i prędkość (gdy domyślne nie działa)
| Flaga | Znaczenie |
|-------|-----------|
| `--port /dev/ttyUSB0` | Port szeregowy (auto: ttyUSB0, ttyACM0, serial0) |
| `--baud 115200` | Prędkość (domyślnie 115200) |

---

## 3. Przykłady „wszystko w jednym”

**Audyt BLE+WiFi + API + SIEM (domyślnie):**
```bash
python3 src/scanner.py --ble --wifi --audit --api
```

**ESP32: codzienny raport o 8:00 z mailem (cron):**
```bash
0 8 * * * cd /ścieżka/do/projektu && ./venv/bin/python scripts/esp32_serial_reader.py --out raporty/esp32_$(date +\%Y\%m\%d).json --enrich --duration 300 --report-email twoj@email.me
```

**Scanner (audyt): zaplanowany skan + raport na maila (cron):**  
Pełny audyt (`--audit`) z crona z wysyłką raportu emailem – ta sama konfiguracja SMTP co ESP32 (`.env`, Proton). Raport trafia do `exports/combined_report_*.json` i jako załącznik na podany adres.
```bash
# Codziennie o 3:00, raport emailem (SMTP z .env)
0 3 * * * cd /ścieżka/do/projektu && ./venv/bin/python src/scanner.py --audit --report-email twoj@email.me 2>&1 | logger -t scanner-audit

# Raz w tygodniu (niedziela 3:00) z mailem
0 3 * * 0 cd /ścieżka/do/projektu && ./venv/bin/python src/scanner.py --audit --report-email twoj@email.me 2>&1 | logger -t scanner-audit
```
Zamień `/ścieżka/do/projektu` i `twoj@email.me` na swoje. Konfiguracja Proton/SMTP: [CRON_PROTON_ESP32.md](CRON_PROTON_ESP32.md).

**ESP32: test 5 min + mail (ręcznie):**
```bash
python3 scripts/esp32_serial_reader.py --out raporty/test.json --enrich --duration 300 --report-email twoj@email.me
```

---

## 4. Konfiguracja (SMTP dla raportów/alertów)

W `.env` w katalogu projektu (np. Proton):
```env
SMTP_SERVER=smtp.protonmail.ch
SMTP_PORT=587
SMTP_USER=adres@domena.pl
SMTP_PASSWORD=token_smtp
EMAIL_FROM=adres@domena.pl
```

Pełna instrukcja: [CRON_PROTON_ESP32.md](CRON_PROTON_ESP32.md).

---

Wszystkie flagi: [FLAGI.md](FLAGI.md).
