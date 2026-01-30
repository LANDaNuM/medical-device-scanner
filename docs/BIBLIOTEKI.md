# 📚 Biblioteki i Ich Wyjaśnienia

## 🎯 Core Dependencies

### `python-dotenv>=1.0.0`
**Co robi:** Ładuje zmienne środowiskowe z pliku `.env`
**Do czego:** Przechowywanie API keys i konfiguracji (np. `NVD_API_KEY`, `VIRUSTOTAL_API_KEY`)
**Przykład:** `load_dotenv()` ładuje zmienne z `.env` do `os.environ`

---

## 📡 Skanowanie Protokołów

### `bleak>=0.21.0`
**Co robi:** Biblioteka do skanowania Bluetooth Low Energy (BLE)
**Do czego:** Wykrywanie urządzeń BLE, analiza GATT services, sprawdzanie szyfrowania
**Platformy:** Linux, Windows, macOS
**Użycie:** `src/real_scanner.py` - skanowanie urządzeń medycznych przez Bluetooth

### `scapy>=2.5.0`
**Co robi:** Biblioteka do manipulacji pakietami sieciowymi
**Do czego:** Skanowanie sieci, analiza pakietów, ARP scan
**Użycie:** `src/wifi_scanner.py` - wykrywanie urządzeń w sieci lokalnej

### `python-nmap>=0.7.1`
**Co robi:** Python wrapper dla nmap (Network Mapper)
**Do czego:** Skanowanie portów TCP/UDP, wykrywanie usług, identyfikacja systemów operacyjnych
**Wymaga:** `nmap` zainstalowany w systemie (`sudo apt-get install nmap`)
**Użycie:** `src/wifi_scanner.py` - skanowanie portów medycznych (DICOM, HL7)

### `pyusb>=1.2.1`
**Co robi:** Biblioteka do komunikacji z urządzeniami USB
**Do czego:** Wykrywanie urządzeń USB, odczyt Vendor ID/Product ID
**Wymaga:** Uprawnienia do urządzeń USB (może wymagać `sudo` lub udev rules)
**Użycie:** `src/usb_scanner.py` - skanowanie urządzeń medycznych podłączonych przez USB

### `pyserial>=3.5`
**Co robi:** Biblioteka do komunikacji z portami szeregowymi (COM)
**Do czego:** Wykrywanie portów szeregowych, komunikacja z urządzeniami przez COM
**Użycie:** `src/usb_scanner.py` - analiza portów szeregowych

### `nfcpy>=1.0.4`
**Co robi:** Biblioteka do komunikacji z czytnikami NFC
**Do czego:** Skanowanie kart i tagów NFC, analiza właściwości kart inteligentnych
**Wymaga:** Czytnik NFC (np. ACR122U) i biblioteki systemowe PCSC
**Użycie:** `src/nfc_scanner.py` - skanowanie urządzeń/kart NFC

---

## 📊 Przetwarzanie Danych

### `pandas>=2.0.0`
**Co robi:** Biblioteka do analizy i manipulacji danymi strukturalnymi
**Do czego:** Przetwarzanie danych urządzeń, eksport do CSV, analiza statystyczna
**Użycie:** `src/dashboard.py`, `src/anomaly_detector.py` - analiza danych

### `numpy>=1.24.0`
**Co robi:** Biblioteka do obliczeń numerycznych i operacji na macierzach
**Do czego:** Operacje matematyczne, wektoryzacja, ekstrakcja cech ML
**Użycie:** `src/anomaly_detector.py` - przetwarzanie cech dla ML

---

## 🤖 AI/ML

### `scikit-learn>=1.3.0`
**Co robi:** Biblioteka Machine Learning dla Pythona
**Do czego:** 
- **Isolation Forest** - wykrywanie anomalii
- **Local Outlier Factor (LOF)** - wykrywanie lokalnych anomalii
- **One-Class SVM** - wykrywanie odstających punktów
- **KMeans, DBSCAN** - klasteryzacja urządzeń
- **Random Forest** - predykcja podatności
- **StandardScaler** - normalizacja danych
**Użycie:** `src/anomaly_detector.py` - wszystkie algorytmy ML

### `tensorflow>=2.13.0` (Opcjonalne)
**Co robi:** Framework Deep Learning
**Do czego:** Autoencoder do wykrywania złożonych wzorców anomalii
**Użycie:** `src/anomaly_detector.py` - Deep Learning (opcjonalne, jeśli zainstalowane)
**Instalacja:** `pip install tensorflow>=2.13.0`

---

## 🎨 Dashboard i Wizualizacja

### `streamlit>=1.28.0`
**Co robi:** Framework do szybkiego tworzenia aplikacji webowych w Pythonie
**Do czego:** Interaktywny dashboard do wizualizacji wyników skanowania
**Użycie:** `src/dashboard.py` - dashboard webowy
**Uruchomienie:** `streamlit run src/dashboard.py`

### `plotly>=5.17.0`
**Co robi:** Biblioteka do interaktywnych wizualizacji
**Do czego:** Wykresy, wykresy scatter, histogramy, pie charts
**Użycie:** `src/dashboard.py` - wizualizacje statystyk i wykrytych anomalii

---

## 🌐 Backend i API

### `flask>=3.0.0`
**Co robi:** Framework webowy do tworzenia REST API
**Do czego:** REST API serwer do dostępu do danych skanera
**Użycie:** `src/api_server.py` - endpointy `/devices`, `/report`, `/stats`

### `flask-cors>=4.0.0`
**Co robi:** Rozszerzenie Flask do obsługi CORS (Cross-Origin Resource Sharing)
**Do czego:** Umożliwia dostęp do API z innych domen (np. frontend aplikacji)
**Użycie:** `src/api_server.py` - umożliwia cross-origin requests

### `gunicorn>=21.2.0`
**Co robi:** Production WSGI HTTP Server
**Do czego:** Uruchamianie aplikacji Flask w środowisku produkcyjnym
**Użycie:** Production deployment (np. na Render.com)

---

## 💾 Baza Danych

### `sqlalchemy>=2.0.0`
**Co robi:** ORM (Object-Relational Mapping) dla Pythona
**Do czego:** Zarządzanie bazą danych, zapytania SQL przez Python
**Użycie:** Możliwość rozszerzenia o bazę danych (obecnie nie używane)

---

## 📄 Raportowanie

### `reportlab>=4.0.0`
**Co robi:** Biblioteka do generowania dokumentów PDF
**Do czego:** Generowanie raportów PDF z wynikami skanowania
**Użycie:** `src/scanner.py` - generowanie raportów PDF

### `matplotlib>=3.7.0`
**Co robi:** Biblioteka do tworzenia wykresów statycznych
**Do czego:** Wykresy w raportach PDF
**Użycie:** `src/scanner.py` - wizualizacje w raportach

---

## 🛠️ Utilities

### `pydantic>=2.0.0`
**Co robi:** Biblioteka do walidacji danych używając type hints
**Do czego:** Walidacja danych wejściowych, type checking
**Użycie:** Możliwość walidacji danych urządzeń

### `rich>=13.0.0`
**Co robi:** Biblioteka do pięknego wyświetlania w terminalu
**Do czego:** Kolorowe tabele, panele, progress bars w terminalu
**Użycie:** `src/scanner.py`, wszystkie skanery - wyświetlanie wyników w terminalu

### `requests>=2.31.0`
**Co robi:** Biblioteka do wykonywania żądań HTTP
**Do czego:** Integracja z zewnętrznymi API (NIST NVD, VirusTotal, Shodan)
**Użycie:** `src/cve_lookup.py`, `src/external_apis.py` - pobieranie danych z API

### `mac-vendor-lookup>=0.1.12`
**Co robi:** Biblioteka do identyfikacji producenta po adresie MAC
**Do czego:** Określanie producenta urządzenia na podstawie OUI (Organizationally Unique Identifier)
**Użycie:** `src/oui_lookup.py` - identyfikacja producentów urządzeń

---

## 📦 Instalacja Wszystkich Bibliotek

```bash
# Aktywuj virtual environment
source venv/bin/activate

# Zainstaluj wszystkie biblioteki
pip install -r requirements.txt
```

## 🔍 Sprawdzenie Zainstalowanych Bibliotek

```bash
pip list
```

---

## 🦀 Biblioteki Rust (dla modułu rust_scanner)

**Uwaga:** Te biblioteki są używane w module Rust (`rust_scanner/`), nie w Pythonie.  
Są kompilowane razem z kodem Rust przez `maturin`.

### `pyo3>=0.20`
**Co robi:** Biblioteka do integracji Rust z Pythonem
**Do czego:** Pozwala na wywoływanie kodu Rust z Pythona
**Features:** `extension-module` (moduł Python), `abi3-py38` (kompatybilność z Python 3.8+)
**Użycie:** `rust_scanner/src/lib.rs` - integracja Rust z Pythonem

### `tokio>=1.35`
**Co robi:** Asynchroniczny runtime dla Rust
**Do czego:** Równoległe skanowanie portów, async I/O
**Features:** `full` (wszystkie funkcjonalności)
**Użycie:** `rust_scanner/src/lib.rs` - asynchroniczne skanowanie portów TCP

### `serde>=1.0` + `serde_json>=1.0`
**Co robi:** Serializacja/deserializacja danych w Rust
**Do czego:** Konwersja danych między Rust a Pythonem (przez JSON)
**Użycie:** `rust_scanner/src/lib.rs` - przetwarzanie danych urządzeń

**Instalacja Rust bibliotek:**
```bash
# Rust biblioteki są instalowane automatycznie przez cargo podczas:
maturin develop
```

---

## ⚠️ Uwagi

- **TensorFlow** jest opcjonalne - potrzebne tylko dla Deep Learning (Autoencoder)
- **nmap** musi być zainstalowany w systemie (nie przez pip): `sudo apt-get install nmap`
- **Czytnik NFC** wymaga bibliotek systemowych: `sudo apt-get install libpcsclite-dev`
- **USB** może wymagać uprawnień: dodaj użytkownika do grupy `dialout` lub użyj `sudo`
- **reportlab** jest wymieniony 2x w requirements.txt (linia 41 i 47) - to duplikacja, ale nie szkodzi
- **Biblioteki Rust** (pyo3, tokio, serde) są instalowane automatycznie przez `maturin develop`
