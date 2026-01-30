# 🖥️ Wymagania Sprzętowe - Medical Device Scanner

## 📋 Podsumowanie

| Protokół | Laptop/PC | Raspberry Pi | Telefon | Dodatkowy Sprzęt |
|----------|-----------|--------------|---------|------------------|
| **BLE** | ✅ Działa | ✅ Działa | ✅ Działa | ❌ Nie wymaga |
| **WiFi** | ✅ Działa | ✅ Działa | ❌ Wymaga root | ❌ Nie wymaga |
| **USB** | ✅ Działa | ✅ Działa | ❌ Nie działa | ❌ Nie wymaga |
| **NFC** | ⚠️ Wymaga czytnika | ⚠️ Wymaga czytnika | ⚠️ Ograniczone | ✅ **Czytnik NFC** |

---

## 💻 Opcja 1: Laptop/PC (ZALECANE)

### ✅ Co Działa:

#### 📡 BLE (Bluetooth Low Energy)
- **Wymagania:** Wbudowany Bluetooth (większość laptopów ma)
- **Dodatkowe:** ❌ Nie wymaga
- **Test:** `python src/scanner.py --ble`

#### 📶 WiFi
- **Wymagania:** Karta sieciowa WiFi (wbudowana w laptopach)
- **Dodatkowe:** ❌ Nie wymaga
- **Test:** `python src/scanner.py --wifi`
- **Uwaga:** Może wymagać `sudo` dla niektórych funkcji (ARP scan)

#### 🔌 USB
- **Wymagania:** Porty USB (wbudowane w laptopach)
- **Dodatkowe:** ❌ Nie wymaga
- **Test:** `python src/scanner.py --usb`
- **Uwaga:** Może wymagać uprawnień dla niektórych urządzeń

#### 📱 NFC
- **Wymagania:** ❌ **Wymaga czytnika NFC** (np. ACR122U)
- **Dodatkowe:** ✅ **Czytnik NFC** (~50-100 PLN)
- **Test:** `python src/scanner.py --nfc`

### 💰 Koszt:
- **Laptop/PC:** Masz już (0 PLN)
- **Czytnik NFC (opcjonalnie):** ~50-100 PLN
- **RAZEM:** 0-100 PLN

---

## 🍓 Opcja 2: Raspberry Pi

### ✅ Co Działa:

#### 📡 BLE (Bluetooth Low Energy)
- **Wymagania:** Raspberry Pi 3/4/5 (mają wbudowany Bluetooth)
- **Dodatkowe:** ❌ Nie wymaga
- **Test:** `python src/scanner.py --ble`

#### 📶 WiFi
- **Wymagania:** Raspberry Pi 3/4/5 (mają wbudowany WiFi)
- **Dodatkowe:** ❌ Nie wymaga
- **Test:** `python src/scanner.py --wifi`

#### 🔌 USB
- **Wymagania:** Porty USB (wbudowane w Raspberry Pi)
- **Dodatkowe:** ❌ Nie wymaga
- **Test:** `python src/scanner.py --usb`

#### 📱 NFC
- **Wymagania:** ❌ **Wymaga czytnika NFC** (np. ACR122U)
- **Dodatkowe:** ✅ **Czytnik NFC** (~50-100 PLN)
- **Test:** `python src/scanner.py --nfc`

### 💰 Koszt:
- **Raspberry Pi 4:** ~200-300 PLN
- **Karta SD (32GB):** ~30 PLN
- **Zasilacz:** ~30 PLN
- **Obudowa (opcjonalnie):** ~30 PLN
- **Czytnik NFC (opcjonalnie):** ~50-100 PLN
- **RAZEM:** ~340-490 PLN

### 🎯 Zalety Raspberry Pi:
- ✅ Niski pobór mocy (można zostawić włączone 24/7)
- ✅ Mały rozmiar (łatwo ukryć)
- ✅ Tani (tańszy niż laptop)
- ✅ Idealny do monitorowania ciągłego

---

## 📱 Opcja 3: Telefon (Android/iOS)

### ⚠️ Ograniczenia:

#### 📡 BLE (Bluetooth Low Energy)
- **Status:** ✅ **DZIAŁA**
- **Wymagania:** Wbudowany Bluetooth (wszystkie telefony mają)
- **Test:** Można uruchomić skaner BLE

#### 📶 WiFi
- **Status:** ❌ **NIE DZIAŁA** (bez root)
- **Problem:** Android/iOS blokują skanowanie portów innych urządzeń
- **Rozwiązanie:** Użyj Web Interface (uruchom na komputerze, otwórz w przeglądarce)

#### 🔌 USB
- **Status:** ❌ **NIE DZIAŁA**
- **Problem:** Telefony nie mają USB Host Mode (wymaga OTG + specjalnych sterowników)

#### 📱 NFC
- **Status:** ⚠️ **OGRANICZONE**
- **Problem:** Biblioteka `nfcpy` wymaga PC/SC (nie dostępne na Androidzie/iOS)
- **Rozwiązanie:** Użyj natywnych API Android/iOS (wymaga osobnej aplikacji)

### 💰 Koszt:
- **Telefon:** Masz już (0 PLN)
- **RAZEM:** 0 PLN (ale ograniczona funkcjonalność)

---

## 🎯 Rekomendacja dla Ćwiczeń

### ✅ **OPCJA 1: Laptop/PC (NAJLEPSZA)**

**Dlaczego:**
- ✅ Masz już laptop/PC
- ✅ Wszystko działa (BLE, WiFi, USB)
- ✅ Łatwa instalacja i debugowanie
- ✅ Możesz ćwiczyć wszystkie protokoły

**Co potrzebujesz:**
- Laptop/PC z:
  - Bluetooth (dla BLE)
  - WiFi (dla WiFi)
  - Porty USB (dla USB)
  - Python 3.8+ (zainstalowany)

**Instalacja:**
```bash
# 1. Sklonuj projekt
git clone <repo>

# 2. Utwórz venv
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Zainstaluj zależności
pip install -r requirements.txt

# 4. Uruchom skaner
python src/scanner.py --ble    # Tylko BLE
python src/scanner.py --wifi  # Tylko WiFi
python src/scanner.py          # Wszystkie protokoły
```

---

### ✅ **OPCJA 2: Raspberry Pi (DO MONITOROWANIA)**

**Dlaczego:**
- ✅ Niski pobór mocy (można zostawić włączone 24/7)
- ✅ Mały rozmiar (łatwo ukryć)
- ✅ Tani (tańszy niż laptop)
- ✅ Idealny do ciągłego monitorowania

**Co potrzebujesz:**
- Raspberry Pi 3/4/5 (z WiFi i Bluetooth)
- Karta SD (32GB minimum)
- Zasilacz
- (Opcjonalnie) Czytnik NFC

**Instalacja:**
```bash
# 1. Zainstaluj Raspberry Pi OS
# 2. Zainstaluj Python 3.8+
sudo apt-get update
sudo apt-get install python3-pip python3-venv

# 3. Sklonuj projekt
git clone <repo>

# 4. Utwórz venv
python3 -m venv venv
source venv/bin/activate

# 5. Zainstaluj zależności
pip install -r requirements.txt

# 6. Uruchom skaner
python src/scanner.py --monitor  # Ciągłe monitorowanie
```

---

## 🔧 Szczegółowe Wymagania Sprzętowe

### 📡 BLE (Bluetooth Low Energy)

#### Minimalne Wymagania:
- **Bluetooth 4.0+** (wbudowany w większość laptopów)
- **Biblioteka:** `bleak` (działa na Linux/Windows/Mac)

#### Test Sprzętu:
```bash
# Linux
bluetoothctl --version  # Sprawdź czy Bluetooth działa

# Windows
# Otwórz Ustawienia → Urządzenia → Bluetooth

# Mac
# Otwórz Preferencje Systemowe → Bluetooth
```

#### Co Można Skanować:
- ✅ Glukometry Bluetooth
- ✅ Pulsoksymetry Bluetooth
- ✅ Opaski fitness
- ✅ Smartwatche z funkcjami medycznymi
- ✅ Wszystkie urządzenia BLE w zasięgu

---

### 📶 WiFi

#### Minimalne Wymagania:
- **Karta sieciowa WiFi** (wbudowana w laptopach)
- **Biblioteka:** `scapy`, `python-nmap`
- **Narzędzie:** `nmap` (do skanowania portów)

#### Instalacja:
```bash
# Linux
sudo apt-get install nmap

# Mac
brew install nmap

# Windows
# Pobierz z: https://nmap.org/download.html
```

#### Co Można Skanować:
- ✅ Urządzenia w sieci lokalnej (192.168.x.x)
- ✅ Porty medyczne (DICOM 104, HL7 5000)
- ✅ Usługi sieciowe (HTTP, HTTPS, SSH)
- ✅ Urządzenia IoT w sieci

#### Uwaga:
- Może wymagać `sudo` dla niektórych funkcji (ARP scan)
- Bez `sudo` działa podstawowe skanowanie (ping + socket)

---

### 🔌 USB

#### Minimalne Wymagania:
- **Porty USB** (wbudowane w laptopach)
- **Biblioteka:** `pyusb`, `pyserial`
- **Uprawnienia:** Może wymagać `sudo` lub udev rules

#### Instalacja:
```bash
# Linux - dodaj użytkownika do grupy dialout (dla portów szeregowych)
sudo usermod -a -G dialout $USER

# Linux - udev rules (dla USB)
# Utwórz plik: /etc/udev/rules.d/99-usb.rules
# Zawartość: SUBSYSTEM=="usb", MODE="0666"
```

#### Co Można Skanować:
- ✅ Urządzenia USB podłączone do komputera
- ✅ Porty szeregowe (COM)
- ✅ Vendor ID / Product ID
- ✅ Urządzenia medyczne podłączone przez USB

---

### 📱 NFC

#### Minimalne Wymagania:
- ❌ **Czytnik NFC** (np. ACR122U) - **WYMAGANY**
- **Biblioteka:** `nfcpy`, `pyscard`
- **Biblioteka systemowa:** PC/SC (libpcsclite)

#### Instalacja:
```bash
# Linux
sudo apt-get install libpcsclite-dev pcscd

# Mac
brew install pcsc-lite

# Windows
# PC/SC jest wbudowany w Windows
```

#### Czytniki NFC (Rekomendowane):
- **ACR122U** (~50-100 PLN) - najpopularniejszy
- **ACR1252U** (~100-150 PLN) - bardziej zaawansowany
- **PN532** (~30-50 PLN) - tani, ale wymaga więcej konfiguracji

#### Co Można Skanować:
- ✅ Karty NFC (karty pacjentów)
- ✅ Tagi NFC (identyfikatory urządzeń)
- ✅ Karty inteligentne (smart cards)

---

## 💡 Co Można Zrobić BEZ Dodatkowego Sprzętu?

### ✅ Symulacja (Dla Ćwiczeń)

Możesz ćwiczyć kod **bez prawdziwego sprzętu** używając symulacji:

```python
# Przykład: Symulacja skanera BLE
class MockBLEScanner:
    def scan(self):
        return [
            Device("AA:BB:CC:DD:EE:01", "Glukometr Symulowany", 80, True),
            Device("AA:BB:CC:DD:EE:02", "Pompa Symulowana", 60, False),
        ]
```

**Zalety:**
- ✅ Nie wymaga sprzętu
- ✅ Można ćwiczyć kod
- ✅ Szybkie testy
- ✅ Idealne do nauki

**Wady:**
- ❌ Nie skanuje prawdziwych urządzeń
- ❌ Nie testuje prawdziwego sprzętu

---

## 🎓 Dla Ćwiczeń - Minimalne Wymagania

### ✅ **OPCJA MINIMALNA (0 PLN):**

**Co potrzebujesz:**
- Laptop/PC (masz już)
- Python 3.8+ (darmowy)
- Internet (do pobrania bibliotek)

**Co możesz ćwiczyć:**
- ✅ Kod skanera (symulacja)
- ✅ Analiza bezpieczeństwa
- ✅ Generowanie raportów
- ✅ API i backend

**Co NIE możesz ćwiczyć:**
- ❌ Prawdziwe skanowanie BLE (wymaga Bluetooth)
- ❌ Prawdziwe skanowanie WiFi (wymaga sieci)
- ❌ Prawdziwe skanowanie USB (wymaga urządzeń USB)
- ❌ Prawdziwe skanowanie NFC (wymaga czytnika)

---

### ✅ **OPCJA PODSTAWOWA (0 PLN):**

**Co potrzebujesz:**
- Laptop/PC z **Bluetooth** (większość ma)
- Python 3.8+

**Co możesz ćwiczyć:**
- ✅ **Prawdziwe skanowanie BLE** (urządzenia Bluetooth w zasięgu)
- ✅ Kod skanera
- ✅ Analiza bezpieczeństwa
- ✅ Generowanie raportów

**Co NIE możesz ćwiczyć:**
- ❌ Prawdziwe skanowanie WiFi (wymaga sieci, może wymagać sudo)
- ❌ Prawdziwe skanowanie USB (wymaga urządzeń USB)
- ❌ Prawdziwe skanowanie NFC (wymaga czytnika)

---

### ✅ **OPCJA PEŁNA (0-100 PLN):**

**Co potrzebujesz:**
- Laptop/PC z Bluetooth i WiFi
- Python 3.8+
- (Opcjonalnie) Czytnik NFC (~50-100 PLN)

**Co możesz ćwiczyć:**
- ✅ **Prawdziwe skanowanie BLE** (urządzenia Bluetooth)
- ✅ **Prawdziwe skanowanie WiFi** (urządzenia w sieci)
- ✅ **Prawdziwe skanowanie USB** (urządzenia USB)
- ✅ (Opcjonalnie) **Prawdziwe skanowanie NFC** (z czytnikiem)
- ✅ Wszystkie funkcje skanera

---

## 📊 Porównanie Opcji

| Opcja | Koszt | BLE | WiFi | USB | NFC | Dla Ćwiczeń |
|-------|-------|-----|------|-----|-----|-------------|
| **Minimalna** | 0 PLN | ❌ | ❌ | ❌ | ❌ | ✅ Symulacja |
| **Podstawowa** | 0 PLN | ✅ | ❌ | ❌ | ❌ | ✅ BLE |
| **Pełna** | 0-100 PLN | ✅ | ✅ | ✅ | ⚠️ | ✅ Wszystko |
| **Raspberry Pi** | ~340 PLN | ✅ | ✅ | ✅ | ⚠️ | ✅ Monitorowanie |

---

## 🎯 Rekomendacja

### Dla Ćwiczeń:
**Użyj LAPTOP/PC** (masz już, 0 PLN)
- ✅ Wszystko działa (BLE, WiFi, USB)
- ✅ Łatwa instalacja
- ✅ Idealne do nauki

### Dla Monitorowania:
**Użyj RASPBERRY PI** (~340 PLN)
- ✅ Niski pobór mocy
- ✅ Można zostawić włączone 24/7
- ✅ Idealny do ciągłego monitorowania

### Dla Pełnej Funkcjonalności:
**LAPTOP/PC + Czytnik NFC** (0-100 PLN)
- ✅ Wszystkie protokoły
- ✅ Pełna funkcjonalność

---

## ❓ FAQ

### Czy mogę ćwiczyć bez sprzętu?
**TAK!** Możesz używać symulacji do ćwiczenia kodu. Prawdziwe skanowanie wymaga sprzętu.

### Czy potrzebuję czytnika NFC?
**NIE!** Czytnik NFC jest opcjonalny. Możesz ćwiczyć wszystkie inne protokoły bez niego.

### Czy Raspberry Pi jest lepszy niż laptop?
**Zależy od celu:**
- **Ćwiczenia:** Laptop (łatwiejszy)
- **Monitorowanie:** Raspberry Pi (tańszy, mniejszy pobór mocy)

### Czy mogę użyć telefonu?
**TAK, ale ograniczone:**
- ✅ BLE działa
- ❌ WiFi wymaga root
- ❌ USB nie działa
- ⚠️ NFC wymaga osobnej aplikacji

**Lepsze rozwiązanie:** Uruchom na komputerze, otwórz Web Interface w przeglądarce telefonu.

---

## 📝 Podsumowanie

**Dla ćwiczeń potrzebujesz:**
- ✅ Laptop/PC (masz już)
- ✅ Python 3.8+ (darmowy)
- ✅ Internet (do pobrania bibliotek)

**Opcjonalnie:**
- ⚠️ Czytnik NFC (~50-100 PLN) - tylko jeśli chcesz testować NFC

**RAZEM:** 0-100 PLN (w zależności od potrzeb)

---

**Powodzenia w ćwiczeniach! 🚀**
