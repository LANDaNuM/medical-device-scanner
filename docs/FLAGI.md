# 📋 Flagi i Opcje Skanera

Krótki przewodnik po wszystkich dostępnych flagach.

## 🚀 Podstawowe Użycie

```bash
# Skanuj wszystko (automatycznie)
python3 src/scanner.py

# Skanuj tylko wybrane protokoły
python3 src/scanner.py --wifi
python3 src/scanner.py --ble --usb
python3 src/scanner.py --wifi --usb --nfc
```

## 🔍 Flagi Skanowania

| Flaga | Opis |
|-------|------|
| `--ble` | Skanuj tylko Bluetooth Low Energy |
| `--wifi` | Skanuj tylko WiFi (sieć lokalna) |
| `--usb` | Skanuj tylko USB (urządzenia podłączone) |
| `--nfc` | Skanuj tylko NFC (karty i tagi) |
| `--no-wifi` | Pomiń WiFi (tylko urządzenia bezpośrednio podłączone) |

**Uwaga:** Jeśli nie podasz żadnej flagi, skaner automatycznie skanuje wszystkie dostępne protokoły.

## 🔒 Audyt Bezpieczeństwa

| Flaga | Opis |
|-------|------|
| `--audit` | Pełny audyt bezpieczeństwa (testy podatności, port scanning) |

**Przykład:**
```bash
python3 src/scanner.py --wifi --audit
```

## 🌐 API Server

| Flaga | Opis |
|-------|------|
| `--api` | Uruchom API server po skanowaniu (otwiera przeglądarkę) |
| `--api-port PORT` | Port dla API server (domyślnie: 5000) |

**Przykład:**
```bash
python3 src/scanner.py --api
python3 src/scanner.py --api --api-port 8080
```

**Uwaga:** Po zamknięciu przeglądarki skanowanie automatycznie się kończy.

## 📤 Automatyczne Funkcje (Domyślnie Włączone)

Skaner automatycznie wykonuje:

1. **Eksport do SIEM** - format JSON Lines (uniwersalny dla ELK Stack)
   - Plik: `siem_export_YYYYMMDD_HHMMSS.jsonl`
   - Wyłącz: `--no-siem`

2. **Threat Intelligence** - sprawdzanie IP w bazach zagrożeń
   - Wymaga klucza API (AbuseIPDB, VirusTotal, Shodan)
   - Plik: `threat_intel_YYYYMMDD_HHMMSS.json`
   - Wyłącz: `--no-threat-intel`

3. **Historia skanowań** - automatyczne zapisywanie do bazy danych SQLite
   - Plik: `history.db`
   - Zawsze włączone (automatyczne)

**Wyłączanie automatycznych funkcji:**
```bash
# Bez SIEM i Threat Intelligence
python3 src/scanner.py --no-siem --no-threat-intel

# Tylko bez Threat Intelligence
python3 src/scanner.py --no-threat-intel
```

## 📅 Zaplanowane Skanowania

| Flaga | Opis |
|-------|------|
| `--schedule SCHEDULE` | Zaplanuj skanowanie (np. "daily 09:00", "hourly", "every 30 minutes") |

**Przykłady:**
```bash
# Codziennie o 9:00
python3 src/scanner.py --schedule "daily 09:00"

# Co godzinę
python3 src/scanner.py --schedule "hourly"

# Co 30 minut
python3 src/scanner.py --schedule "every 30 minutes"
```

## 📧 Powiadomienia Email

| Flaga | Opis |
|-------|------|
| `--email EMAIL ...` | Wyślij raport emailem po skanowaniu |
| `--email-alerts EMAIL ...` | Adresy email do alertów (z monitoringiem) |

**Wymaga konfiguracji w `.env`:**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=twoj_email@gmail.com
SMTP_PASSWORD=twoje_haslo
EMAIL_FROM=twoj_email@gmail.com
```

**Przykłady:**
```bash
# Wyślij raport emailem
python3 src/scanner.py --email admin@hospital.com

# Do wielu odbiorców
python3 src/scanner.py --email admin@hospital.com security@hospital.com
```

## 🔍 Real-time Monitoring

| Flaga | Opis |
|-------|------|
| `--monitor` | Uruchom monitoring w czasie rzeczywistym |
| `--interval SECONDS` | Interwał monitoringu w sekundach (domyślnie 300 = 5 minut) |

**Przykłady:**
```bash
# Monitoring co 5 minut (domyślnie)
python3 src/scanner.py --monitor

# Monitoring co 1 minutę
python3 src/scanner.py --monitor --interval 60

# Z alertami email
python3 src/scanner.py --monitor --email-alerts admin@hospital.com
```

## 📡 Mikrokontroler (ESP32)

Odbiornik danych z ESP32 podłączonego do Raspberry Pi przez USB (port szeregowy). ESP32 wysyła wyniki skanów BLE i WiFi jako linie JSON. **Skrypt:** `scripts/esp32_serial_reader.py`.

**Wymagania:** ESP32 podłączone kablem USB do Pi (lub PC), na ESP32 wgrany program np. `ESP32_Unified_Scanner.ino`.

| Flaga | Opis |
|-------|------|
| `--port PORT` | Port szeregowy, np. `/dev/ttyUSB0` lub `/dev/ttyACM0` (domyślnie: auto – szuka ttyUSB0, ttyACM0, serial0) |
| `--baud BAUD` | Prędkość portu w bodach (domyślnie: 115200) |
| `--out PLIK` | Zapisuj każdą linię do pliku (np. `wyniki_esp32.json`) – plik jest **nadpisywany** przy każdym uruchomieniu |
| `--enrich` | Wzbogacanie: producent (OUI), typ urządzenia z UUID, podpowiedzi podatności (`ble_bez_parowania`, `możliwe_urządzenie_medyczne`) |
| `--on-new-scan` | Przy zdarzeniu **new** (BLE) uruchom skaner: `python src/scanner.py --ble` (co najwyżej co 60 s) |
| `--alert-email ADR` | Wyślij email przy **nowym urządzeniu** (SMTP z `.env`: SMTP_SERVER, SMTP_USER, SMTP_PASSWORD) |
| `--alert-slack URL` | Wyślij POST do **Slack Incoming Webhook** przy nowym urządzeniu |
| `--alert-splunk PLIK` | Dopisz linię do pliku przy nowym urządzeniu (Splunk monitoruje ten plik) |

**Przykłady:**
```bash
# Tylko podgląd w terminalu
python3 scripts/esp32_serial_reader.py

# Zapis do pliku + wzbogacanie
python3 scripts/esp32_serial_reader.py --out wyniki_esp32.json --enrich

# Przy nowym BLE uruchom skaner (co najwyżej co 60 s)
python3 scripts/esp32_serial_reader.py --out wyniki_esp32.json --enrich --on-new-scan

# Alert email przy nowym urządzeniu (SMTP w .env)
python3 scripts/esp32_serial_reader.py --out wyniki_esp32.json --enrich --alert-email admin@example.com

# Alert do Slack
python3 scripts/esp32_serial_reader.py --out wyniki_esp32.json --alert-slack https://hooks.slack.com/services/XXX

# Dopisanie do pliku dla Splunk
python3 scripts/esp32_serial_reader.py --out wyniki_esp32.json --alert-splunk /var/log/splunk_esp32.jsonl
```

**Uwaga:** Przed wgrywaniem nowego firmware na ESP32 (Arduino IDE lub esptool) zatrzymaj skrypt (Ctrl+C), żeby port nie był zajęty.

---

## 📊 Przykłady Kombinacji

```bash
# Szybkie skanowanie WiFi z audytem
python3 src/scanner.py --wifi --audit

# Pełne skanowanie z API (bez automatycznych funkcji)
python3 src/scanner.py --api --no-siem --no-threat-intel

# Skanowanie USB i BLE z API
python3 src/scanner.py --usb --ble --api

# Codzienne skanowanie z raportem emailem
python3 src/scanner.py --schedule "daily 09:00" --email admin@hospital.com

# Monitoring z alertami
python3 src/scanner.py --monitor --interval 300 --email-alerts admin@hospital.com
```

## 🎯 Najczęściej Używane

```bash
# Standardowe skanowanie (wszystko automatycznie)
python3 src/scanner.py

# Skanowanie WiFi z API (najpopularniejsze)
python3 src/scanner.py --wifi --api

# Pełny audyt bezpieczeństwa
python3 src/scanner.py --audit

# Codzienne skanowanie z raportem emailem
python3 src/scanner.py --schedule "daily 09:00" --email admin@hospital.com

# Monitoring w czasie rzeczywistym
python3 src/scanner.py --monitor --interval 300
```

## ⚙️ Konfiguracja API Keys

Aby użyć Threat Intelligence, dodaj klucze API do pliku `.env`:

```bash
# Threat Intelligence
ABUSEIPDB_API_KEY=twoj_klucz  # Darmowe: https://www.abuseipdb.com/pricing

# Opcjonalne (już istniejące)
VIRUSTOTAL_API_KEY=twoj_klucz
SHODAN_API_KEY=twoj_klucz
```

## 📝 Pliki Wyjściowe

Skaner automatycznie generuje:

- `scan_YYYYMMDD_HHMMSS.json` - Wyniki skanowania
- `report_YYYYMMDD_HHMMSS.json` - Pełny raport
- `siem_export_YYYYMMDD_HHMMSS.jsonl` - Eksport SIEM (automatycznie)
- `threat_intel_YYYYMMDD_HHMMSS.json` - Threat Intelligence (automatycznie, jeśli API dostępne)

## 💡 Wskazówki

1. **Pierwsze skanowanie:** Użyj `python3 src/scanner.py` - skanuje wszystko automatycznie
2. **Szybkie skanowanie:** `--wifi` - tylko sieć lokalna
3. **Bez WiFi:** `--no-wifi` - pomija skanowanie sieci (szybsze)
4. **Z API:** `--api` - otwiera przeglądarkę z wynikami
5. **Bez automatycznych funkcji:** `--no-siem --no-threat-intel` - jeśli nie potrzebujesz
6. **Mikrokontroler ESP32:** `python3 scripts/esp32_serial_reader.py --out wyniki_esp32.json --enrich` – odbiór BLE/WiFi z ESP32 przez USB

## ❓ Pomoc

```bash
python3 src/scanner.py --help
```
