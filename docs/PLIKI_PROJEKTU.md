# 📁 Pliki Projektu - Opis Co Robi Każdy Plik

## 🐍 Pliki Python (.py)

### `src/scanner.py` ⭐ **GŁÓWNY PLIK**
**Co robi:** Główny moduł skanera - łączy wszystkie komponenty
- Zarządza skanowaniem wszystkich protokołów (BLE, WiFi, USB, NFC)
- Analizuje bezpieczeństwo urządzeń
- Wykrywa anomalie używając ML
- Generuje raporty (JSON, CSV, PDF)
- Wyświetla wyniki w terminalu

**Uruchomienie:** `python3 src/scanner.py`

---

### `src/device.py`
**Co robi:** Model danych - reprezentuje urządzenie medyczne
- Klasa `Device` - przechowuje informacje o urządzeniu
- `DeviceType` - enum z typami urządzeń (glukometr, pompa insulinowa, etc.)
- `Protocol` - enum z protokołami (BLE, WiFi, USB, NFC)
- Metody: `calculate_security_score()`, `to_dict()`, `add_vulnerability()`

**Użycie:** Importowany przez inne moduły, nie uruchamiany bezpośrednio

---

### `src/real_scanner.py`
**Co robi:** Prawdziwy skaner Bluetooth Low Energy (BLE)
- Skanuje rzeczywiste urządzenia BLE w zasięgu
- Wykrywa szyfrowanie na podstawie GATT services i characteristics
- Analizuje advertising data (flags, services)
- Próbuje połączyć się bez parowania (sprawdza czy wymaga parowania)
- Wykrywa urządzenia medyczne po UUID serwisów (np. 0x1808 dla Glucose Service)
- Używa biblioteki `bleak` (działa na Linux/Windows/Mac)
- Asynchroniczne skanowanie

**Użycie:** Używany przez `scanner.py` do skanowania BLE

---

### `src/wifi_scanner.py`
**Co robi:** Skaner urządzeń WiFi w sieci lokalnej
- Skanuje urządzenia w sieci (ping, ARP scan, nmap)
- Analizuje otwarte porty TCP/UDP
- Wykrywa porty medyczne (DICOM 104, HL7 11112, PACS 5000)
- Sprawdza szyfrowanie (HTTPS vs HTTP)
- Identyfikuje usługi (SSH, RDP, HTTP, etc.)
- Może używać Rust do szybkiego skanowania portów (jeśli dostępny)

**Użycie:** Używany przez `scanner.py` do skanowania WiFi

---

### `src/usb_scanner.py`
**Co robi:** Skaner urządzeń USB podłączonych do komputera
- Wykrywa urządzenia USB (Vendor ID, Product ID)
- Analizuje porty szeregowe (COM)
- Sprawdza czy urządzenie może być medyczne

**Użycie:** Używany przez `scanner.py` do skanowania USB

---

### `src/nfc_scanner.py`
**Co robi:** Skaner urządzeń NFC (karty, tagi)
- Skanuje karty i tagi NFC
- Wymaga czytnika NFC (np. ACR122U)
- Analizuje właściwości kart inteligentnych

**Użycie:** Używany przez `scanner.py` do skanowania NFC

---

### `src/vulnerability_tester.py`
**Co robi:** Testowanie podatności i symulacja ataków
- Wykonuje szczegółowe testy podatności
- Sprawdza konfigurację bezpieczeństwa
- Symuluje ataki (bez faktycznego atakowania)
- Testuje porty medyczne (DICOM, HL7) i standardowe (SSH, RDP, etc.)
- Używa CVE i znanych exploity (przez `cve_lookup.py`)
- Wykrywa słabe hasła, otwarte porty, nieaktualne oprogramowanie
- Dzieli podatności na: Krytyczna, Wysoka, Średnia, Niska

**Użycie:** Używany przez `scanner.py` z flagą `--audit`

---

### `src/encryption_analyzer.py`
**Co robi:** Analiza szyfrowania urządzeń
- Analizuje typ szyfrowania (AES-128, WPA2, TLS, etc.)
- Określa siłę szyfrowania (strong/moderate/weak/none)
- Wykrywa słabe algorytmy
- Daje rekomendacje

**Użycie:** Używany przez `scanner.py` podczas analizy bezpieczeństwa

---

### `src/cve_lookup.py`
**Co robi:** Wyszukiwanie aktualnych podatności CVE
- Integruje się z NIST NVD API (darmowe)
- Pobiera aktualne podatności dla otwartych portów/usług
- CVSS scores, daty publikacji, szczegółowe opisy
- Cache lokalny (24h) dla szybkiego działania
- Fallback do lokalnej bazy gdy API nie jest dostępne
- Mapuje porty na usługi (np. 22→SSH, 3389→RDP, 104→DICOM)

**Użycie:** Używany przez `vulnerability_tester.py` i `scanner.py`

---

### `src/external_apis.py`
**Co robi:** Integracja z zewnętrznymi API
- VirusTotal API - sprawdzanie reputacji IP
- Shodan API - wyszukiwanie informacji o urządzeniach
- Wzbogaca dane o urządzeniach

**Użycie:** Używany przez `scanner.py` do wzbogacania danych

---

### `src/oui_lookup.py`
**Co robi:** Identyfikacja producenta po adresie MAC
- Używa OUI (Organizationally Unique Identifier)
- Określa producenta urządzenia na podstawie MAC address
- Używa biblioteki `mac-vendor-lookup`

**Użycie:** Używany przez skanery do identyfikacji producentów

---

### `src/anomaly_detector.py`
**Co robi:** Machine Learning - wykrywanie anomalii
- Używa algorytmów ML: Isolation Forest, LOF, One-Class SVM
- Deep Learning (Autoencoder) - opcjonalnie
- Wykrywanie w czasie rzeczywistym (streaming)
- Predykcja przyszłych podatności
- Klasteryzacja urządzeń
- Integracja z SIEM
- Wykrywa nietypowe urządzenia na podstawie cech bezpieczeństwa
- Ensemble method - głosowanie większościowe
- Automatyczny trening modelu
- Zapisywanie/wczytywanie modelu

**Użycie:** Automatycznie używany przez `scanner.py` (jeśli >= 10 urządzeń)

---

### `src/dashboard.py`
**Co robi:** Dashboard webowy do wizualizacji
- Interaktywny dashboard (Streamlit)
- Wizualizacje (wykresy, statystyki) - Plotly
- Wykrywanie anomalii (ML)
- Filtrowanie urządzeń
- Eksport danych do CSV

**Uruchomienie:** `streamlit run src/dashboard.py`

---

### `src/api_server.py`
**Co robi:** REST API serwer (Flask)
- REST API do dostępu do danych skanera
- Endpointy: `/devices`, `/report`, `/stats`
- HTML interface dla przeglądarki
- Filtrowanie, paginacja, sortowanie

**Uruchomienie:** `python3 src/api_server.py`

---

### `src/rust_scanner_wrapper.py`
**Co robi:** Wrapper do modułu Rust
- Integruje Rust z Pythonem
- Automatyczny fallback do Python (jeśli Rust niedostępny)
- Klasy: `FastPortScanner`, `DeviceProcessor`
- Sprawdza dostępność Rust: `is_rust_available()`

**Użycie:** Używany przez inne moduły do szybkiego skanowania portów

---

### `src/__init__.py`
**Co robi:** Plik inicjalizacyjny Pythona
- Oznacza katalog `src/` jako pakiet Python
- Zawiera metadane pakietu (wersja, autor)
- Może zawierać importy modułów (opcjonalnie)

**Użycie:** Automatycznie używany przez Python przy imporcie pakietu

---

## 🦀 Pliki Rust (.rs)

### `rust_scanner/src/lib.rs` ⭐ **GŁÓWNY PLIK RUST**
**Co robi:** Cały kod Rust - moduł Python
- `FastPortScanner` - szybkie skanowanie portów TCP (3-4x szybsze niż Python)
  - Równoległe skanowanie z semaforem (ograniczenie równoległości)
  - Używa Tokio do async I/O
  - Skanuje porty na IP lub wiele IP jednocześnie
- `DeviceProcessor` - przetwarzanie danych urządzeń (5x szybsze)
  - Przetwarza urządzenia w batchach
  - Oblicza statystyki bezpieczeństwa
- Funkcje pomocnicze: `fast_scan_ports()`
- Integracja z Pythonem przez PyO3

**Klasy i metody:**
```rust
FastPortScanner:
  - new(timeout_ms, max_concurrent)  // Konstruktor
  - scan_ports(ip, ports)            // Skanuje porty na IP
  - scan_multiple_ips(ips, ports)    // Skanuje wiele IP

DeviceProcessor:
  - new(batch_size)                  // Konstruktor
  - process_devices(devices)         // Przetwarza urządzenia
  - calculate_security_stats(devices)  // Statystyki
```

**Użycie:** Kompilowany przez `maturin develop`, dostępny jako `import rust_scanner`

---

## 📊 Podsumowanie - Co Który Plik Robi

| Plik | Typ | Główne Zadanie |
|------|-----|----------------|
| `scanner.py` | Python | ⭐ Główny skaner - łączy wszystko |
| `device.py` | Python | Model danych - reprezentacja urządzenia |
| `real_scanner.py` | Python | Skanowanie BLE (Bluetooth) |
| `wifi_scanner.py` | Python | Skanowanie WiFi |
| `usb_scanner.py` | Python | Skanowanie USB |
| `nfc_scanner.py` | Python | Skanowanie NFC |
| `vulnerability_tester.py` | Python | Testy podatności |
| `encryption_analyzer.py` | Python | Analiza szyfrowania |
| `cve_lookup.py` | Python | Wyszukiwanie CVE |
| `external_apis.py` | Python | Integracja z API (VirusTotal, Shodan) |
| `oui_lookup.py` | Python | Identyfikacja producenta (MAC) |
| `anomaly_detector.py` | Python | ML - wykrywanie anomalii |
| `dashboard.py` | Python | Dashboard webowy |
| `api_server.py` | Python | REST API serwer |
| `rust_scanner_wrapper.py` | Python | Wrapper Rust |
| `__init__.py` | Python | Inicjalizacja pakietu |
| `lib.rs` | Rust | Szybkie skanowanie portów (Rust) |

---

## 🔄 Przepływ Danych

```
scanner.py (główny)
    ↓
    ├─→ real_scanner.py (BLE)
    ├─→ wifi_scanner.py (WiFi)
    ├─→ usb_scanner.py (USB)
    ├─→ nfc_scanner.py (NFC)
    ↓
device.py (model danych)
    ↓
    ├─→ encryption_analyzer.py (analiza szyfrowania)
    ├─→ vulnerability_tester.py (testy podatności)
    │   └─→ cve_lookup.py (CVE)
    ├─→ external_apis.py (wzbogacanie danych)
    ├─→ anomaly_detector.py (ML)
    └─→ rust_scanner_wrapper.py
        └─→ lib.rs (Rust - szybkie skanowanie)
    ↓
Raporty (JSON, CSV, PDF)
```

---

## 🎯 Które Pliki Są Najważniejsze?

1. **`scanner.py`** - Główny plik, uruchamiasz go
2. **`device.py`** - Model danych, używany przez wszystkie moduły
3. **`lib.rs`** - Rust moduł, działa w tle (szybsze skanowanie)
4. **`anomaly_detector.py`** - ML, automatycznie używany
5. **`dashboard.py`** - Dashboard, opcjonalny

---

## 💡 Krótkie Wyjaśnienie

- **Skanery** (`real_scanner.py`, `wifi_scanner.py`, etc.) - wykrywają urządzenia
- **Analizatory** (`encryption_analyzer.py`, `vulnerability_tester.py`) - analizują bezpieczeństwo
- **ML** (`anomaly_detector.py`) - wykrywa anomalie
- **Rust** (`lib.rs`) - szybkie operacje (skanowanie portów)
- **UI** (`dashboard.py`, `api_server.py`) - interfejsy użytkownika
