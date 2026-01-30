# 📡 Przykłady ESP32 dla Medical Device Scanner

Ten folder zawiera przykładowe kody Arduino dla ESP32, które można wykorzystać do testowania skanera urządzeń medycznych.

## 📋 Dostępne Przykłady

### 1. `ESP32_Glukometr_BLE.ino`
Symuluje glukometr Bluetooth Low Energy używając standardowego UUID medycznego (0x1808 - Glucose Service).

**Funkcje:**
- ✅ Standardowy UUID medyczny (Glucose Service)
- ✅ Symuluje pomiary glukozy (70-120 mg/dL)
- ✅ Wykrywany przez skaner jako urządzenie medyczne
- ✅ Notifications przez BLE

**Użycie:**
1. Wgraj kod na ESP32
2. Uruchom skaner: `python src/scanner.py --ble`
3. ESP32 zostanie wykryte jako glukometr

---

### 2. `ESP32_WiFi_Medical_Server.ino`
Tworzy serwer HTTP na ESP32 symulujący urządzenie medyczne z danymi witalnymi.

**Funkcje:**
- ✅ Serwer HTTP z danymi witalnymi (puls, saturacja, temperatura)
- ✅ API endpoints: `/api/vitals`, `/api/device/info`, `/api/health`
- ✅ Web interface (HTML)
- ✅ Wykrywany przez skaner WiFi

**Użycie:**
1. Zmień SSID i hasło WiFi w kodzie
2. Wgraj kod na ESP32
3. Sprawdź IP w Serial Monitor
4. Uruchom skaner: `python src/scanner.py --wifi`
5. Otwórz w przeglądarce: `http://<IP_ESP32>`

**Endpoints:**
- `GET /` - Web interface
- `GET /api/vitals` - JSON z danymi witalnymi
- `GET /api/device/info` - Informacje o urządzeniu
- `GET /api/health` - Status urządzenia

---

### 3. `ESP32_Unified_Scanner.ino` – **jeden plik: BLE + WiFi, wiele urządzeń (zalecane)**
Jeden program zamiast kilku – nie musisz co chwilę wgrywać innego pliku. Skanuje **BLE** (telefony, słuchawki, czujniki, stare urządzenia) oraz **sieci WiFi** (SSID + siła sygnału). Wyniki idą przez **Serial** (podłącz ESP32 do Pi USB i uruchom na Pi: `python scripts/esp32_serial_reader.py`). Opcjonalnie możesz ustawić WiFi i adres serwera – wtedy dane trafiają też na Pi przez sieć; **nie musisz sprawdzać IP w Serial Monitor** – dane idą na adres ustawiony w kodzie.

---

### 4. `ESP32_Agent_Serial.ino` (tylko BLE, przez USB)
Wysyła wyniki skanów BLE do Raspberry Pi przez kabel USB (port szeregowy). Na Pi uruchom: `python scripts/esp32_serial_reader.py`. Działa przy **bezpośrednim podłączeniu** Pi ↔ ESP32 – bez WiFi. Zobacz sekcję „Bezpośrednie podłączenie” w `docs/WYKORZYSTANIE_ESP32_RASPBERRY_PI.md`.

---

### 5. `ESP32_Vulnerable_Device.ino`
**⚠️ CELOWO TWORZY PODATNOŚCI BEZPIECZEŃSTWA!**

Symuluje urządzenie z podatnościami do testowania wykrywania przez skaner.

**Podatności:**
- ❌ Brak szyfrowania BLE
- ❌ Brak autoryzacji (każdy może się połączyć)
- ❌ Dane medyczne dostępne bez hasła
- ❌ Brak wymagania parowania

**Użycie:**
1. Wgraj kod na ESP32
2. Uruchom skaner: `python src/scanner.py --ble`
3. Skaner powinien wykryć podatności:
   - Security Score: ~50/100
   - Wykryte podatności: "Brak szyfrowania", "Brak autoryzacji"

---

## 🛠️ Instalacja i Setup

### Wymagania:
- ESP32 Board (ESP-WROOM-32)
- Arduino IDE
- Kabel USB (USB-C dla ESP32)

### Krok 1: Instalacja ESP32 Board Support

1. Otwórz Arduino IDE
2. Przejdź do: `File` → `Preferences`
3. W polu "Additional Boards Manager URLs" dodaj:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Przejdź do: `Tools` → `Board` → `Boards Manager`
5. Wyszukaj "ESP32" i zainstaluj "esp32 by Espressif Systems"
6. Wybierz board: `Tools` → `Board` → `ESP32 Arduino` → `ESP32 Dev Module`

### Krok 2: Wgranie Kodu

1. Otwórz plik `.ino` w Arduino IDE
2. Podłącz ESP32 przez USB
3. Wybierz port: `Tools` → `Port` → `<COM_PORT>` (Windows) lub `/dev/ttyUSB0` (Linux)
4. Kliknij "Upload" (strzałka w prawo)
5. Sprawdź Serial Monitor: `Tools` → `Serial Monitor` (115200 baud)

### Krok 3: Testowanie

1. Uruchom skaner na Raspberry Pi lub laptopie:
   ```bash
   python src/scanner.py --ble    # Dla BLE
   python src/scanner.py --wifi   # Dla WiFi
   ```
2. Sprawdź czy ESP32 jest wykrywane
3. Sprawdź dashboard: `streamlit run src/dashboard.py`

---

## 📚 Dokumentacja

### Biblioteki ESP32:
- **BLE:** Wbudowana w ESP32 Arduino Core
- **WiFi:** Wbudowana w ESP32 Arduino Core
- **WebServer:** Wbudowana w ESP32 Arduino Core

### Przydatne Linki:
- [ESP32 Arduino Documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/)
- [BLE Examples](https://github.com/espressif/arduino-esp32/tree/master/libraries/BLE/examples)
- [WiFi Examples](https://github.com/espressif/arduino-esp32/tree/master/libraries/WiFi/examples)

---

## 🔧 Rozwiązywanie Problemów

### Problem: ESP32 nie łączy się z WiFi
**Rozwiązanie:**
- Sprawdź SSID i hasło w kodzie
- Upewnij się, że WiFi działa na 2.4GHz (ESP32 nie obsługuje 5GHz)
- Sprawdź odległość od routera

### Problem: BLE nie jest wykrywane
**Rozwiązanie:**
- Upewnij się, że Bluetooth jest włączony na urządzeniu skanującym
- Sprawdź Serial Monitor ESP32 - czy urządzenie się reklamuje?
- Spróbuj zrestartować ESP32

### Problem: Arduino IDE nie widzi ESP32
**Rozwiązanie:**
- Zainstaluj sterowniki CH340 (dla USB-C)
- Sprawdź czy kabel USB obsługuje dane (nie tylko zasilanie)
- Spróbuj innego portu USB

---

## 💡 Pomysły na Rozszerzenie

### 1. Dodaj więcej typów urządzeń:
- Pulsoksymetr BLE
- Pompa insulinowa WiFi
- Monitor ciśnienia krwi

### 2. Dodaj szyfrowanie:
- Włącz BLE encryption
- Dodaj autoryzację (pairing)
- Użyj TLS dla WiFi

### 3. Dodaj więcej danych:
- Historia pomiarów
- Alerty (wysokie/niskie wartości)
- Synchronizacja z chmurą

---

## ⚠️ Uwagi Bezpieczeństwa

**WAŻNE:**
- Przykład `ESP32_Vulnerable_Device.ino` **CELOWO** tworzy podatności
- **NIE używaj** tego kodu w produkcji!
- Używaj **TYLKO** do testowania skanera bezpieczeństwa
- W rzeczywistych urządzeniach medycznych zawsze używaj szyfrowania!

---

## 📝 Licencja

Te przykłady są częścią projektu Medical Device Security Scanner i są dostępne na tej samej licencji co projekt główny.

---

**Powodzenia w testowaniu! 🚀**
