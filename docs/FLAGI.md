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
   - Plik: `exports/siem_export_YYYYMMDD_HHMMSS.jsonl`
   - Wyłącz: `--no-siem`

2. **Threat Intelligence** - sprawdzanie IP w bazach zagrożeń
   - Wymaga klucza API (AbuseIPDB, VirusTotal, Shodan)
   - Dane w `combined_report_*.json` (sekcja `threat_intelligence`)
   - Wyłącz: `--no-threat-intel`

3. **Historia skanowań** - automatyczne zapisywanie do bazy danych SQLite
   - Plik: `history.db`
   - Zawsze włączone (automatyczne)

4. **Combined Report** - kompleksowy raport z wszystkimi danymi
   - Plik: `reports/combined_report_YYYY-MM-DD_HH-MM-SS.json`
   - Zawiera: skanowanie + analiza + threat intelligence
   - Zawsze tworzony (domyślnie)

**Wyłączanie automatycznych funkcji:**
```bash
# Bez SIEM i Threat Intelligence
python3 src/scanner.py --no-siem --no-threat-intel

# Tylko bez Threat Intelligence
python3 src/scanner.py --no-threat-intel
```

## 📄 Raportowanie

| Flaga | Opis |
|-------|------|
| `--legacy-reports` | Twórz również stare pliki (scan_*.json, report_*.json) - domyślnie tylko combined_report_*.json |

**Domyślnie:**
- ✅ `combined_report_*.json` - **ZALECANY** - wszystkie dane w jednym pliku
- ❌ `scan_*.json` - nie tworzony (tylko z `--legacy-reports`)
- ❌ `report_*.json` - nie tworzony (tylko z `--legacy-reports`)

**Z `--legacy-reports`:**
- ✅ `combined_report_*.json` - wszystkie dane
- ✅ `scan_*.json` - surowe dane (duplikat)
- ✅ `report_*.json` - analiza (duplikat)

**Przykład:**
```bash
# Tylko combined_report_*.json (domyślnie)
python3 src/scanner.py

# Z wszystkimi plikami (dla kompatybilności wstecznej)
python3 src/scanner.py --legacy-reports
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

**⚠️ UWAGA:** Flagi email nie są jeszcze zaimplementowane w kodzie. Funkcjonalność jest planowana.

| Flaga | Status | Opis |
|-------|--------|------|
| `--email EMAIL ...` | ⏳ Planowane | Wyślij raport emailem po skanowaniu |
| `--email-alerts EMAIL ...` | ⏳ Planowane | Adresy email do alertów (z monitoringiem) |

**Aktualny status:**
- Funkcjonalność email jest opisana w dokumentacji `FUNKCJONALNOSCI.md`
- Kod nie jest jeszcze zaimplementowany
- Monitor wspiera email_recipients jako parametr, ale nie ma flag CLI

**Gdy będzie dostępne, wymaga konfiguracji w `.env`:**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=twoj_email@gmail.com
SMTP_PASSWORD=twoje_haslo
EMAIL_FROM=twoj_email@gmail.com
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

# Monitoring z interwałem (bez email - email nie jest jeszcze zaimplementowany)
python3 src/scanner.py --monitor --interval 60
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

# Codzienne skanowanie
python3 src/scanner.py --schedule "daily 09:00"

# Monitoring z interwałem
python3 src/scanner.py --monitor --interval 300
```

## 🎯 Najczęściej Używane

```bash
# Standardowe skanowanie (wszystko automatycznie)
python3 src/scanner.py

# Skanowanie WiFi z API (najpopularniejsze)
python3 src/scanner.py --wifi --api

# Pełny audyt bezpieczeństwa
python3 src/scanner.py --audit

# Codzienne skanowanie
python3 src/scanner.py --schedule "daily 09:00"

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

### Domyślnie (Zalecane):
- ✅ `reports/combined_report_YYYY-MM-DD_HH-MM-SS.json` - **ZALECANY** - wszystkie dane w jednym pliku
  - Zawiera: skanowanie + analiza + threat intelligence
- ✅ `exports/siem_export_YYYYMMDD_HHMMSS.jsonl` - Eksport SIEM (automatycznie)
- ✅ `history.db` - Historia skanowań (SQLite)

### Z `--legacy-reports`:
- ✅ `reports/combined_report_*.json` - wszystkie dane
- ✅ `reports/scan_YYYY-MM-DD_HH-MM-SS.json` - Surowe dane (duplikat z combined_report)
- ✅ `reports/report_YYYY-MM-DD_HH-MM-SS.json` - Analiza (duplikat z combined_report)

**Uwaga:** Threat Intelligence jest teraz w `combined_report_*.json` (sekcja `threat_intelligence`), nie w osobnym pliku.

## 💡 Wskazówki

1. **Pierwsze skanowanie:** Użyj `python3 src/scanner.py` - skanuje wszystko automatycznie
2. **Szybkie skanowanie:** `--wifi` - tylko sieć lokalna
3. **Bez WiFi:** `--no-wifi` - pomija skanowanie sieci (szybsze)
4. **Z API:** `--api` - otwiera przeglądarkę z wynikami
5. **Bez automatycznych funkcji:** `--no-siem --no-threat-intel` - jeśli nie potrzebujesz
6. **Mikrokontroler ESP32:** `python3 scripts/esp32_serial_reader.py --out wyniki_esp32.json --enrich` – odbiór BLE/WiFi z ESP32 przez USB

## 📋 Pełna Lista Wszystkich Flag

| Flaga | Typ | Opis | Domyślnie |
|-------|-----|------|-----------|
| `--ble` | boolean | Skanuj tylko Bluetooth Low Energy | ❌ |
| `--wifi` | boolean | Skanuj tylko WiFi (sieć lokalna) | ❌ |
| `--usb` | boolean | Skanuj tylko USB (urządzenia podłączone) | ❌ |
| `--nfc` | boolean | Skanuj tylko NFC (karty i tagi) | ❌ |
| `--no-wifi` | boolean | Pomiń WiFi (tylko urządzenia bezpośrednio podłączone) | ❌ |
| `--audit` | boolean | Pełny audyt bezpieczeństwa (testy podatności) | ❌ |
| `--api` | boolean | Uruchom API server po skanowaniu | ❌ |
| `--api-port PORT` | integer | Port dla API server | 5000 |
| `--no-siem` | boolean | Wyłącz automatyczny eksport do SIEM | ✅ Włączony |
| `--no-threat-intel` | boolean | Wyłącz automatyczne sprawdzanie threat intelligence | ✅ Włączony |
| `--legacy-reports` | boolean | Twórz również stare pliki (scan_*.json, report_*.json) | ❌ |
| `--schedule SCHEDULE` | string | Zaplanuj skanowanie (np. "daily 09:00") | ❌ |
| `--monitor` | boolean | Uruchom monitoring w czasie rzeczywistym | ❌ |
| `--interval SECONDS` | integer | Interwał monitoringu w sekundach | 300 |

**Uwagi:**
- Jeśli nie podasz żadnej flagi protokołu (`--ble`, `--wifi`, etc.), skaner automatycznie skanuje wszystkie dostępne protokoły
- `--no-siem` i `--no-threat-intel` wyłączają funkcje które są domyślnie włączone
- `--legacy-reports` tworzy dodatkowe pliki (duplikaty danych z `combined_report_*.json`)

## ❓ Pomoc

```bash
python3 src/scanner.py --help
```
