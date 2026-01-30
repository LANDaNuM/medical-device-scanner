# 🏥 Medical Device Security Scanner

Narzędzie do audytu bezpieczeństwa urządzeń medycznych IoT.

## 🎯 Cel projektu

Zbudować darmowe, open-source narzędzie do:
- Wykrywania urządzeń medycznych w sieci (Bluetooth, WiFi)
- Analizy ich bezpieczeństwa (szyfrowanie, autoryzacja, podatności)
- Wykrywania anomalii używając AI
- Generowania raportów zgodnych z FDA guidelines

## 📋 Status projektu

- [x] Setup projektu
- [x] Weekend 1: Basic Discovery (BLE, WiFi, USB, NFC)
- [x] Weekend 2: Security Analysis + AI (ML Anomaly Detection)
- [x] Weekend 3: Backend API + Dashboard (Flask API + Streamlit Dashboard)
- [ ] Weekend 4: Polish + Documentation

## 🚀 Szybki start

### Opcja 1: Automatyczny setup (zalecane)

```bash
# Uruchom setup script
./setup.sh

# Aktywuj virtual environment
source venv/bin/activate

# Uruchom skaner
python src/scanner.py
```

### Opcja 2: Ręczna instalacja

```bash
# Utwórz virtual environment
python3 -m venv venv
source venv/bin/activate  # Na Windows: venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom skaner
python src/scanner.py
```

## 🔍 Pełnoprawny Skaner Urządzeń Medycznych

Projekt obsługuje **4 protokoły komunikacji**:

### 📡 BLE (Bluetooth Low Energy)
- ✅ Skanuje rzeczywiste urządzenia Bluetooth w zasięgu
- ✅ Wykrywa szyfrowanie na podstawie GATT services i characteristics
- ✅ Wymaga: `pip install bleak`
- ```bash
  python src/scanner.py --ble
  ```

### 📶 WiFi
- ✅ Skanuje urządzenia w sieci lokalnej
- ✅ Analizuje otwarte porty i usługi (DICOM, HL7)
- ✅ Wymaga: `pip install python-nmap`
- ```bash
  python src/scanner.py --wifi
  ```

### 🔌 USB
- ✅ Wykrywa urządzenia USB podłączone do komputera
- ✅ Analizuje porty szeregowe (COM)
- ✅ Wymaga: `pip install pyusb pyserial`
- ```bash
  python src/scanner.py --usb
  ```

### 📱 NFC
- ✅ Skanuje urządzenia NFC (karty, tagi)
- ✅ Wymaga czytnika NFC (np. ACR122U)
- ✅ Wymaga: `pip install nfcpy pyscard`
- ```bash
  python src/scanner.py --nfc
  ```

### 🚀 Skanuj Wszystkie Protokoły

**ZALECANA KOMENDA (wszystko działa bez sudo):**
```bash
# Upewnij się, że venv jest aktywowany
source venv/bin/activate

# Uruchom skaner (wszystkie protokoły)
python3 src/scanner.py
```

**Co działa:**
- ✅ **BLE**: Działa bez sudo (nie wymaga root)
- ✅ **WiFi**: Działa bez sudo (scapy użyje podstawowego skanowania - ping + socket)
- ✅ **USB**: Działa bez sudo (może wymagać uprawnień dla niektórych urządzeń)
- ✅ **NFC**: Działa bez sudo (wymaga czytnika NFC)

**Dla lepszych wyników WiFi (scapy ARP scan wymaga root):**
```bash
source venv/bin/activate
sudo -E python3 src/scanner.py --wifi  # Tylko WiFi z ARP scan
```

**Uwaga:** `sudo -E` zachowuje zmienne środowiskowe z venv, więc biblioteki będą dostępne.

**Jak wykrywamy szyfrowanie?**
- **BLE**: Analizujemy GATT characteristics, próbujemy połączyć się bez parowania
- **WiFi**: Sprawdzamy porty HTTPS (443, 8443), analizujemy otwarte porty
- **USB**: USB zazwyczaj nie ma szyfrowania na poziomie protokołu (podatność!)
- **NFC**: NFC ma podstawowe szyfrowanie, ale wymaga autoryzacji

📖 **Więcej informacji:** Zobacz `docs/REAL_SCANNER.md`

## 🤖 Machine Learning - Wykrywanie Anomalii

Skaner wykorzystuje **Machine Learning** do automatycznego wykrywania nietypowych urządzeń:

- ✅ **Isolation Forest**: Szybkie wykrywanie anomalii
- ✅ **Local Outlier Factor (LOF)**: Wykrywanie lokalnych anomalii
- ✅ **One-Class SVM**: Wykrywanie odstających wzorców
- ✅ **Ensemble Method**: Głosowanie większościowe dla lepszej dokładności

**Automatyczne wykrywanie**: ML jest automatycznie uruchamiane po skanowaniu (wymaga minimum 10 urządzeń).

```bash
# Normalne skanowanie (automatycznie wykryje anomalie)
python src/scanner.py
```

📖 **Więcej informacji:** Zobacz `docs/ML_AI.md`

## 📊 Dashboard Webowy

Interaktywny dashboard do wizualizacji i analizy urządzeń:

```bash
# Zainstaluj zależności (jeśli jeszcze nie)
pip install streamlit plotly

# Uruchom dashboard
streamlit run src/dashboard.py
```

Dashboard oferuje:
- 📈 Wizualizacje (wykresy, statystyki)
- 🤖 Wykrywanie anomalii (ML)
- 📱 Lista urządzeń z filtrowaniem
- 💾 Eksport danych do CSV

Dashboard będzie dostępny pod adresem: `http://localhost:8501`

## 🦀 Integracja Rust - Wydajność i Bezpieczeństwo

Projekt wykorzystuje **Rust** do wydajnych operacji wymagających bezpieczeństwa pamięci:

- ✅ **Szybkie skanowanie portów TCP** (3-4x szybsze niż Python)
- ✅ **Bezpieczeństwo pamięci** (brak dangling pointers, buffer overflows)
- ✅ **Przewidywalne zużycie pamięci** (brak GC)
- ✅ **Wydajność porównywalna z C/C++**

### Instalacja Rust Module

```bash
# 1. Zainstaluj Rust SYSTEMOWO (nie w venv - to kompilator)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 2. Aktywuj venv
source venv/bin/activate

# 3. Zainstaluj maturin W venv
pip install maturin

# 4. Zbuduj moduł Rust (instaluje do venv)
cd rust_scanner
maturin develop
cd ..
```

**Uwaga:** Rust jest instalowany systemowo, ale zbudowany moduł jest w venv!

### Użycie

```python
from rust_scanner_wrapper import FastPortScanner

# Szybkie skanowanie portów (Rust)
scanner = FastPortScanner(timeout_ms=1000, max_concurrent=50)
open_ports = scanner.scan_ports("192.168.1.1", [22, 80, 443, 3389])
```

**Fallback:** Jeśli Rust nie jest dostępny, automatycznie używa wolniejszej wersji Python.

📖 **Więcej informacji:** Zobacz `docs/RUST_INTEGRATION.md`

## 🔒 Aktualne Podatności CVE

Skaner automatycznie pobiera **aktualne podatności z NIST NVD API** (darmowe):
- ✅ Automatyczne wyszukiwanie CVE dla otwartych portów
- ✅ CVSS scores, daty publikacji, szczegółowe opisy
- ✅ Cache lokalny (24h) dla szybkiego działania
- ✅ Fallback do lokalnej bazy gdy API nie jest dostępne

**Limity zapytań:**
- Bez API key: **5 zapytań/30s** (wystarczy dla większości przypadków)
- Z darmowym API key: **50 zapytań/30s** (10x więcej!)

**Jak uzyskać darmowy API key:**
1. Wejdź na: https://nvd.nist.gov/developers/request-an-api-key
2. Wypełnij formularz (2 minuty)
3. Ustaw: `export NVD_API_KEY="your-key"`
4. Gotowe! Skaner automatycznie wykryje klucz

**Przykład:**
```
Port 3389 (RDP) - znalezione CVE:
  CVE-2019-0708 (BlueKeep): CRITICAL, CVSS 9.8
  CVE-2021-34527 (PrintNightmare): CRITICAL, CVSS 8.8
```

📖 **Więcej informacji:** 
- `docs/CVE_API.md` - Jak działa integracja z CVE API
- `docs/API_KEYS.md` - Jak uzyskać i skonfigurować API keys (darmowe opcje)

## 📚 Dokumentacja

- **`docs/EXPLANATION.md`** - Wyjaśnienie całego kodu
- **`docs/GETTING_STARTED.md`** - Przewodnik dla początkujących
- **`docs/REAL_SCANNER.md`** - Jak działa prawdziwy skaner i wykrywanie szyfrowania (wszystkie protokoły)
- **`docs/PROTOCOLS.md`** - Kompletny przewodnik po protokołach (BLE, WiFi, USB, NFC) z szczegółowymi opisami
- **`docs/INSTALLATION.md`** - Szczegółowe instrukcje instalacji dla wszystkich protokołów
- **`docs/CVE_API.md`** - Integracja z NIST NVD API dla aktualnych podatności CVE
- **`docs/ML_AI.md`** - Machine Learning i wykrywanie anomalii
- **`docs/RUST_INTEGRATION.md`** - Integracja Rust z Pythonem (wydajność i bezpieczeństwo)

## 🔧 Użycie

```bash
# Skanuj wszystkie dostępne protokoły
python src/scanner.py

# Skanuj tylko wybrane protokoły
python src/scanner.py --ble              # Tylko BLE
python src/scanner.py --wifi             # Tylko WiFi
python src/scanner.py --usb              # Tylko USB
python src/scanner.py --nfc              # Tylko NFC
python src/scanner.py --ble --wifi       # BLE i WiFi

# Pomoc
python src/scanner.py --help
```

## 📦 Instalacja Zależności

```bash
# Zainstaluj wszystkie zależności
pip install -r requirements.txt

# Lub tylko wybrane (dla konkretnych protokołów)
pip install bleak              # BLE
pip install python-nmap       # WiFi (wymaga nmap w systemie)
pip install pyusb pyserial    # USB
pip install nfcpy              # NFC (pyscard opcjonalny)
```

**Uwaga:** Niektóre biblioteki wymagają dodatkowych narzędzi systemowych:
- **WiFi:** Wymaga `nmap` (sudo apt-get install nmap)
- **USB:** Może wymagać libusb (sudo apt-get install libusb-1.0-0-dev)
- **NFC:** Wymaga czytnika NFC (pyscard opcjonalny)

📖 **Więcej informacji:** Zobacz `docs/INSTALLATION.md`

## 🔌 Wykorzystanie ESP32 i Raspberry Pi

Projekt wspiera wykorzystanie **ESP32** i **Raspberry Pi** do testowania i rozszerzania funkcjonalności:

### 🍓 Raspberry Pi 5 jako Główny Serwer
- ✅ Idealny do monitorowania 24/7 (niski pobór mocy)
- ✅ Wystarczająca wydajność (8GB RAM, szybki procesor)
- ✅ Wbudowany WiFi i Bluetooth (wszystkie protokoły działają)
- ✅ Hostowanie Dashboard i API

### 📡 ESP32 jako Urządzenie Testowe
- ✅ Symulacja urządzeń medycznych (glukometr, pulsoksymetr)
- ✅ Testowanie wykrywania przez skaner
- ✅ Symulacja podatności bezpieczeństwa
- ✅ Rozszerzanie zasięgu skanowania (distributed scanning)

**Dostępne przykłady:**
- `esp32_examples/ESP32_Glukometr_BLE.ino` - Glukometr BLE
- `esp32_examples/ESP32_WiFi_Medical_Server.ino` - Serwer HTTP z danymi witalnymi
- `esp32_examples/ESP32_Vulnerable_Device.ino` - Urządzenie z podatnościami (do testowania)

📖 **Pełna dokumentacja:** Zobacz `docs/WYKORZYSTANIE_ESP32_RASPBERRY_PI.md`
