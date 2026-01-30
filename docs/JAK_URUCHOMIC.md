# 🚀 Jak Uruchomić Skaner - Krok po Kroku

## 📋 Szybki Start

### KROK 1: Przejdź do katalogu projektu
```bash
cd /home/nfxcstiniq_79/medical-device-scanner
```

### KROK 2: Aktywuj Virtual Environment
```bash
source venv/bin/activate
```

**Lub jeśli nie masz venv:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### KROK 3: Uruchom Skaner
```bash
# Podstawowe skanowanie (wszystkie protokoły)
python3 src/scanner.py
```

---

## 🎯 Różne Opcje Uruchomienia

### 1. Skanowanie Wszystkich Protokołów
```bash
python3 src/scanner.py
```

**Co się dzieje:**
- ✅ Skanuje BLE (Bluetooth)
- ✅ Skanuje WiFi (sieć lokalna)
- ✅ Skanuje USB (urządzenia podłączone)
- ✅ Skanuje NFC (jeśli masz czytnik)
- ✅ Automatycznie wykrywa anomalie ML (jeśli >= 10 urządzeń)
- ✅ Generuje raporty (JSON, CSV, PDF)

### 2. Skanowanie Tylko Wybranych Protokołów
```bash
# Tylko BLE
python3 src/scanner.py --ble

# Tylko WiFi
python3 src/scanner.py --wifi

# BLE i WiFi
python3 src/scanner.py --ble --wifi

# Tylko USB
python3 src/scanner.py --usb

# Tylko NFC
python3 src/scanner.py --nfc
```

### 3. Skanowanie z Pełnym Audytem Bezpieczeństwa
```bash
# Wszystkie protokoły + pełny audyt
python3 src/scanner.py --audit

# WiFi + pełny audyt
python3 src/scanner.py --wifi --audit
```

**Co robi `--audit`:**
- ✅ Wykonuje szczegółowe testy podatności
- ✅ Sprawdza konfigurację bezpieczeństwa
- ✅ Symuluje ataki (bez faktycznego atakowania)
- ✅ Używa CVE i znanych exploity
- ✅ Wykrywa anomalie ML

### 4. Pomoc
```bash
python3 src/scanner.py --help
```

---

## 📊 Co Zobaczysz?

Po uruchomieniu zobaczysz:

```
🏥 Medical Device Security Scanner
Narzędzie do audytu bezpieczeństwa urządzeń medycznych IoT

✅ Skaner BLE gotowy
✅ Skaner WiFi gotowy
✅ Skaner USB gotowy
✅ Skaner NFC gotowy
✅ Detektor anomalii gotowy (będzie trenowany przy pierwszym użyciu)

🔍 Rozpoczynam kompleksowe skanowanie...

📡 Skanowanie Bluetooth Low Energy (BLE)
  ✓ Wykryto: iPhone (AA:BB:CC:DD:EE:FF) - RSSI: -45 dBm

📡 Skanowanie WiFi
  ✓ Wykryto: 192.168.1.1 (Router)

🔒 Analizuję bezpieczeństwo urządzeń...
🤖 Wykrywanie anomalii używając ML...
  Trenowanie modelu ML...
✅ Model wytrenowany na 15 urządzeniach!
✅ Nie wykryto anomalii

✅ Analiza bezpieczeństwa zakończona

📊 Podsumowanie skanowania
Total urządzeń: 15
🔴 Wysokie ryzyko (score < 50): 2
🟡 Średnie ryzyko (50-79): 5
🟢 Niskie ryzyko (≥80): 8

[Wyświetlanie kart urządzeń...]

✅ Zapisano wyniki skanowania: data/scans/scan_2026-01-21_17-30-00.json
✅ Wygenerowano raport JSON: data/reports/report_2026-01-21_17-30-00.json
✅ Wygenerowano raport PDF: data/reports/report_2026-01-21_17-30-00.pdf
✅ Wygenerowano raport CSV: data/reports/report_2026-01-21_17-30-00.csv
```

---

## 📁 Gdzie Są Wyniki?

Wyniki są zapisywane w:

```
data/
├── scans/          # Surowe dane ze skanowania (JSON)
│   └── scan_*.json
└── reports/        # Raporty (JSON, CSV, PDF)
    ├── report_*.json
    ├── report_*.csv
    └── report_*.pdf
```

---

## 🎯 Przykładowe Użycie

### Przykład 1: Szybkie Skanowanie BLE
```bash
python3 src/scanner.py --ble
```
**Czas:** ~10-15 sekund

### Przykład 2: Pełny Audyt WiFi
```bash
python3 src/scanner.py --wifi --audit
```
**Czas:** ~2-5 minut (zależy od liczby urządzeń)

### Przykład 3: Wszystko
```bash
python3 src/scanner.py --audit
```
**Czas:** ~5-10 minut (pełny skan wszystkich protokołów + audyt)

---

## 🎨 Dashboard Webowy

### Uruchomienie Dashboardu
```bash
streamlit run src/dashboard.py
```

**Dashboard będzie dostępny pod:** `http://localhost:8501`

**Funkcjonalności:**
- 📊 Wizualizacje statystyk
- 🔍 Wykrywanie anomalii ML
- 📱 Lista urządzeń z filtrowaniem
- 💾 Eksport danych do CSV

### ⚠️ Uwaga: Komunikat o Email

Przy pierwszym uruchomieniu Streamlit może zapytać o email. **To jest opcjonalne!**

**Możesz:**
- ✅ **Pominąć** - naciśnij Enter lub wpisz cokolwiek (np. `skip@example.com`)
- ✅ **Wpisać dowolny email** - nie jest używany w projekcie, tylko dla statystyk Streamlit
- ✅ **Zignorować** - nie wpływa na działanie dashboardu

**To nie jest wymagane!** Dashboard działa normalnie bez podawania emaila.

---

## 🌐 REST API Serwer

### Uruchomienie API
```bash
python3 src/api_server.py
```

**API będzie dostępne pod:** `http://localhost:5000`

**Endpointy:**
- `GET /devices` - Lista urządzeń
- `GET /report` - Najnowszy raport
- `GET /stats` - Statystyki

---

## ⚠️ Rozwiązywanie Problemów

### Problem: "ModuleNotFoundError"
**Rozwiązanie:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: "Permission denied" (dla WiFi)
**Rozwiązanie:**
```bash
sudo -E python3 src/scanner.py --wifi
```

### Problem: "BLE scanner niedostępny"
**Rozwiązanie:**
```bash
pip install bleak
```

### Problem: "WiFi scanner niedostępny"
**Rozwiązanie:**
```bash
pip install python-nmap
sudo apt-get install nmap  # Linux
```

---

## ✅ Checklist Przed Uruchomieniem

- [ ] ✅ Jestem w katalogu projektu
- [ ] ✅ venv jest aktywowany (`source venv/bin/activate`)
- [ ] ✅ Zależności są zainstalowane (`pip install -r requirements.txt`)
- [ ] ✅ Mam uprawnienia (dla WiFi może być potrzebne sudo)

---

## 🚀 Gotowe!

Teraz możesz uruchomić:

```bash
python3 src/scanner.py
```

**To wszystko!** Skaner automatycznie:
- ✅ Skanuje wszystkie dostępne protokoły
- ✅ Analizuje bezpieczeństwo
- ✅ Wykrywa anomalie ML
- ✅ Generuje raporty
