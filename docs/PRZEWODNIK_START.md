# 🚀 Przewodnik Startowy - ESP32 + Raspberry Pi

## 📋 Co Potrzebujesz (Razem: ~460 PLN)

1. **ESP32** (~60 PLN) - symulacja urządzeń BLE
2. **Raspberry Pi 4** (~300 PLN) - symulacja sieci medycznych
3. **Czytnik NFC** (~50 PLN) - opcjonalnie (PN532) lub pomiń na początku

---

## 🛒 Krok 1: Zakup Sprzętu

### ESP32 (Wymagany)

**Gdzie kupić:**
- Allegro: Szukaj "ESP32 Development Board"
- Amazon: "ESP32 ESP-WROOM-32"
- Sklepy elektroniczne: Botland, Kamami

**Co kupić:**
- ESP32 Development Board (z USB-C lub micro USB)
- **Kabel USB (do programowania)** - zobacz szczegóły poniżej
- **Koszt:** ~50-70 PLN (ESP32) + ~10-20 PLN (kabel)

**Rekomendowane modele:**
- ESP32-WROOM-32 (najpopularniejszy)
- ESP32-DevKitC (dobry do nauki)

**✅ Przykład dobrego ESP32:**
- **ESP32-WROOM-32 z USB-C i CH340** (Allegro)
- Zawiera: ESP32-WROOM-32, USB-C, CH340 (przetwornik USB), WiFi + Bluetooth
- **Cena:** ~30-50 PLN
- **Link:** https://allegro.pl/oferta/mikrokontroler-esp-wroom-32-esp32-usb-c-ch340-wifi-bt-esp-32-4mb-do-arduino
- **Uwaga:** ESP32-WROOM-32 to idealny model do symulacji urządzeń BLE medycznych!

### 🔌 Kabel USB do Programowania ESP32

**Jaki kabel potrzebujesz:**
- **ESP32 z USB-C:** Kabel **USB-C do USB-A** (lub USB-C do USB-C jeśli laptop ma USB-C)
- **ESP32 z micro USB:** Kabel **micro USB do USB-A**

**⚠️ WAŻNE:** 
- Kabel musi **przesyłać dane** (nie tylko ładować)!
- Unikaj tanich kabli "tylko do ładowania"
- Najlepiej: kabel z USB 2.0 lub 3.0 (przesyła dane)

**Gdzie kupić (Polskie sklepy):**

**Opcja 1: USB-C do USB-A (dla ESP32 z USB-C)**
- **Allegro:** 
  - Kategoria: https://allegro.pl/kategoria/kable-usb-c-124297
  - Szukaj: "kabel USB-C USB-A dane" lub "kabel USB-C USB-A 1m"
  - **Cena:** ~10-25 PLN
- **Botland.pl:** https://botland.com.pl/kable-usb/ - kable USB-C
- **Kamami.pl:** https://kamami.pl/kable-usb - kable USB-C
- **Avt.pl:** https://avt.pl/kable-usb - kable USB-C

**Opcja 2: micro USB do USB-A (dla ESP32 z micro USB)**
- **Allegro:**
  - Kategoria: https://allegro.pl/kategoria/kable-usb-micro-124298
  - Szukaj: "kabel micro USB USB-A dane" lub "kabel micro USB USB-A 1m"
  - **Cena:** ~5-15 PLN
- **Botland.pl:** https://botland.com.pl/kable-usb/ - kable micro USB
- **Kamami.pl:** https://kamami.pl/kable-usb - kable micro USB

**💡 Rekomendacja:**
- **Dla ESP32 z USB-C:** Kup kabel USB-C do USB-A (~15 PLN) na Allegro
- **Dla ESP32 z micro USB:** Kup kabel micro USB do USB-A (~10 PLN) na Allegro
- **Długość:** 1-2 metry wystarczy (nie potrzebujesz długiego kabla)
- **Jakość:** Nie musi być markowy, ale musi przesyłać dane (nie tylko ładować)

**🔍 Jak sprawdzić czy kabel przesyła dane:**
- Po podłączeniu ESP32 do komputera, w Arduino IDE powinien pojawić się port COM (Windows) lub /dev/ttyUSB0 (Linux)
- Jeśli port się nie pojawia, kabel może być "tylko do ładowania"
- **Test:** Podłącz ESP32 → Otwórz Arduino IDE → Narzędzia → Port → Powinien być widoczny port COM

**❌ CZĘSTY BŁĄD - NIE KUPUJ TEGO:**
- **USB-A do USB-A** - ❌ NIE DZIAŁA (oba końce są takie same)
- **USB-C do USB-C** - ⚠️ Działa tylko jeśli laptop ma USB-C
- **Tylko do ładowania** - ❌ NIE DZIAŁA (nie przesyła danych)

**✅ WŁAŚCIWY KABEL:**
- **USB-C do USB-A** - ✅ DZIAŁA (USB-C do ESP32, USB-A do komputera)
- **micro USB do USB-A** - ✅ DZIAŁA (micro USB do ESP32, USB-A do komputera)

**💡 Przykład właściwego kabla na Allegro:**
- Szukaj: "kabel USB-C USB-A dane" lub "kabel USB-C USB-A programowanie"
- **NIE szukaj:** "USB-A do USB-A" (to nie zadziała!)

**✅ Przykład dobrego kabla:**
- **Unitek Y-C474BK USB-A do USB-C 3.1** (Allegro)
- **Specyfikacja:** USB-A (do komputera) → USB-C (do ESP32)
- **Prędkość:** 5 Gbps (USB 3.1) - przesyła dane!
- **Długość:** 1m - wystarczająca
- **Cena:** ~15-25 PLN
- **Link:** https://allegro.pl/oferta/kabel-unitek-y-c474bk-usb-a-usb-c-3-1-5-gbps-1-m
- **Uwaga:** ✅ To jest właściwy kabel! USB-A do USB-C, przesyła dane (nie tylko ładuje)

---

### Raspberry Pi 4 lub 5 (Wymagany)

**Gdzie kupić:**
- Allegro: Szukaj "Raspberry Pi 4" lub "Raspberry Pi 5"
- Amazon: "Raspberry Pi 4 Model B" lub "Raspberry Pi 5"
- Sklepy elektroniczne: Botland, Kamami

**Co kupić:**
- **Raspberry Pi 4 Model B** (4GB RAM wystarczy) - tańsza opcja
- **Raspberry Pi 5** (4GB lub 8GB RAM) - nowsza, szybsza opcja
- Karta SD (32GB minimum, klasa 10) lub microSD (dla Pi 5)
- Zasilacz USB-C (5V, 3A dla Pi 4) lub zasilacz 27W (dla Pi 5)
- Obudowa (opcjonalnie, ale zalecane)
- **Koszt:** ~250-400 PLN (Pi 4) lub ~400-600 PLN (Pi 5)

**Rekomendowane zestawy:**
- Raspberry Pi 4 Starter Kit (zawiera wszystko) - tańsza opcja
- Raspberry Pi 5 Starter Kit (zawiera wszystko) - nowsza opcja

**✅ Przykład dobrego zestawu Pi 4:**
- **Zestaw justPi z Raspberry Pi 4B WiFi 4GB RAM** (Allegro Lokalnie)
- Zawiera: Raspberry Pi 4B, karta 32GB, zasilacz 5V/3A, obudowa z wentylatorami, kable
- **Cena:** ~389 PLN
- **Link:** https://allegrolokalnie.pl/oferta/zestaw-justpi-z-raspberry-pi-4b-wifi-4gb-ram-karta-32gb-zasilacz-kable
- **Uwaga:** Zawiera wszystko co potrzebne, gotowy do użycia!

**✅ Przykład dobrego zestawu Pi 5:**
- **Raspberry Pi 5 8GB Zestaw Startowy 128GB Edition** (Allegro)
- Zawiera: Raspberry Pi 5 (8GB RAM), karta 128GB, zasilacz 27W, kable microHDMI
- **Cena:** ~600-700 PLN (droższe, ale nowsze i szybsze)
- **Link:** https://allegro.pl/oferta/raspberry-pi-5-8-gb-zestaw-startowy-128-gb-edition
- **Zalety:** Szybszy procesor, więcej RAM, nowszy model
- **Uwaga:** Raspberry Pi 5 jest kompatybilne z wszystkimi projektami, ale wymaga zasilacza 27W (nie 5V/3A)

**💡 Które wybrać?**
- **Raspberry Pi 4 (4GB):** ~389 PLN - wystarczy do symulacji serwerów medycznych
- **Raspberry Pi 5 (8GB):** ~600-700 PLN - szybsze, więcej RAM, lepsze do zaawansowanych projektów
- **Rekomendacja:** Jeśli budżet pozwala, Raspberry Pi 5 jest lepsze, ale Pi 4 też wystarczy!

---

### Czytnik NFC (Opcjonalnie)

**Uwaga:** Czytniki NFC są droższe niż wcześniej szacowane. Możesz zacząć bez czytnika NFC - skaner będzie działał dla BLE i WiFi.

**Gdzie kupić:**
- Allegro: Szukaj "NFC Reader" lub "Czytnik NFC"
- Amazon: "NFC Reader USB"
- Sklepy elektroniczne: Botland, Kamami

**Opcja 1: ACR122U (Profesjonalny)**
- **Koszt:** ~200-300 PLN (realistyczna cena)
- **Zalety:** Profesjonalny, najlepsze wsparcie, gotowy do użycia
- **Wady:** Drogi

**Opcja 2: PN532 NFC Module (TAŃSZA - REKOMENDOWANA)**
- **Koszt:** ~40-80 PLN
- **Zalety:** Tani, działa z Raspberry Pi/ESP32, wystarczający do nauki
- **Wady:** Wymaga przewodów i konfiguracji
- **Link:** Szukaj "PN532 NFC Module" na Allegro

**Opcja 3: RC522 RFID Reader (NAJTAŃSZA)**
- **Koszt:** ~15-30 PLN
- **Zalety:** Bardzo tani, łatwa integracja z ESP32/Raspberry Pi
- **Wady:** Głównie RFID (może odczytywać niektóre karty NFC)
- **Link:** Szukaj "RC522 RFID" na Allegro

**💡 Rekomendacja:**
- **Dla nauki:** Zacznij BEZ czytnika NFC (możesz ćwiczyć BLE i WiFi) - **0 PLN**
- **Gdy będziesz potrzebować:** Kup PN532 (~50 PLN) - tani i wystarczający
- **Dla profesjonalnego użycia:** ACR122U (~250 PLN) - gdy będziesz zarabiać

---

## 🔧 Krok 2: Przygotowanie ESP32 (Symulacja BLE)

### 2.1. Instalacja Arduino IDE

**Pobierz:**
- Arduino IDE: https://www.arduino.cc/en/software
- Lub PlatformIO (bardziej zaawansowane): https://platformio.org/

**Instalacja ESP32 w Arduino IDE:**
1. Otwórz Arduino IDE
2. Plik → Preferencje
3. W "Additional Board Manager URLs" dodaj:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Narzędzia → Płyta → Menedżer płytek
5. Szukaj "ESP32" i zainstaluj

---

### 2.2. Programowanie ESP32 jako Symulator Glukometru

**Utwórz nowy plik w Arduino IDE:**

```cpp
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLECharacteristic *pGlucoseCharacteristic;
bool deviceConnected = false;

// UUID dla Glucose Service (standard medyczny Bluetooth)
#define SERVICE_UUID        "1808"  // Glucose Service
#define CHARACTERISTIC_UUID "2A18"  // Glucose Measurement

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
        Serial.println("Urządzenie połączone");
    }

    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
        Serial.println("Urządzenie rozłączone");
    }
};

void setup() {
    Serial.begin(115200);
    Serial.println("Symulator Glukometru BLE - Start");
    
    // Inicjalizuj BLE
    BLEDevice::init("Glukometr-Symulator");
    BLEServer *pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());
    
    // Utwórz Glucose Service
    BLEService *pService = pServer->createService(SERVICE_UUID);
    
    // Utwórz Glucose Measurement Characteristic
    pGlucoseCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    
    pGlucoseCharacteristic->addDescriptor(new BLE2902());
    
    // Uruchom serwis
    pService->start();
    
    // Rozpocznij advertising
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();
    
    Serial.println("Symulator gotowy! Szukaj 'Glukometr-Symulator' w skanerze BLE");
}

void loop() {
    if (deviceConnected) {
        // Symuluj odczyty glukozy (70-180 mg/dL - normalny zakres)
        int glucose = random(70, 180);
        
        // Format danych zgodny ze standardem Bluetooth
        uint8_t data[2];
        data[0] = glucose & 0xFF;
        data[1] = (glucose >> 8) & 0xFF;
        
        pGlucoseCharacteristic->setValue(data, 2);
        pGlucoseCharacteristic->notify();
        
        Serial.print("Wysłano odczyt glukozy: ");
        Serial.print(glucose);
        Serial.println(" mg/dL");
        
        delay(5000); // Co 5 sekund
    }
    delay(1000);
}
```

**Jak wgrać kod:**
1. Podłącz ESP32 do komputera przez USB
2. W Arduino IDE: Narzędzia → Płyta → ESP32 Arduino → ESP32 Dev Module
3. Wybierz port COM (Windows) lub /dev/ttyUSB0 (Linux)
4. Kliknij "Upload"
5. Otwórz Serial Monitor (115200 baud) - zobaczysz logi

---

### 2.3. Test ESP32

**Uruchom skaner:**
```bash
# W katalogu projektu
source venv/bin/activate
python src/scanner.py --ble
```

**Powinieneś zobaczyć:**
```
✓ Wykryto: Glukometr-Symulator (XX:XX:XX:XX:XX:XX)
```

---

## 🍓 Krok 3: Przygotowanie Raspberry Pi (Symulacja Sieci)

### 3.1. Instalacja Raspberry Pi OS

**Pobierz:**
- Raspberry Pi Imager: https://www.raspberrypi.org/software/
- Raspberry Pi OS (Lite lub Desktop)

**Instalacja:**
1. Uruchom Raspberry Pi Imager
2. Wybierz Raspberry Pi OS
3. Wybierz kartę SD
4. Kliknij "Write"
5. Po zakończeniu, włącz Raspberry Pi

---

### 3.2. Konfiguracja Raspberry Pi

**Pierwsze uruchomienie:**
```bash
# Zaloguj się (domyślnie: użytkownik 'pi', hasło 'raspberry')
# Zmień hasło:
passwd

# Zaktualizuj system:
sudo apt-get update
sudo apt-get upgrade -y

# Zainstaluj Python i narzędzia:
sudo apt-get install -y python3-pip python3-venv git
```

---

### 3.3. Instalacja Skanera na Raspberry Pi

```bash
# Sklonuj projekt (lub skopiuj z komputera)
git clone <twoje-repo>
cd medical-device-scanner

# Utwórz venv
python3 -m venv venv
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt
```

---

### 3.4. Symulacja Serwera DICOM na Raspberry Pi

**Utwórz plik `simulator_dicom.py`:**

```python
#!/usr/bin/env python3
"""
Symulator serwera DICOM na Raspberry Pi
Port 104 - standardowy port DICOM
"""

from flask import Flask, jsonify, request
import random
from datetime import datetime

app = Flask(__name__)

# Symulowane dane pacjentów
patients = [
    {"id": "PAT001", "name": "Jan Kowalski", "age": 45},
    {"id": "PAT002", "name": "Anna Nowak", "age": 32},
    {"id": "PAT003", "name": "Piotr Wiśniewski", "age": 58},
]

studies = [
    {"id": "STUDY001", "patient_id": "PAT001", "modality": "CT", "date": "2026-01-18"},
    {"id": "STUDY002", "patient_id": "PAT002", "modality": "MRI", "date": "2026-01-18"},
    {"id": "STUDY003", "patient_id": "PAT003", "modality": "X-Ray", "date": "2026-01-18"},
]

@app.route('/dicom/studies', methods=['GET'])
def get_studies():
    """Symuluj endpoint DICOM - lista badań"""
    return jsonify({
        "status": "success",
        "studies": studies,
        "count": len(studies)
    })

@app.route('/dicom/patient/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Symuluj endpoint DICOM - dane pacjenta"""
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if patient:
        return jsonify({
            "status": "success",
            "patient": patient
        })
    return jsonify({"status": "error", "message": "Patient not found"}), 404

@app.route('/dicom/echo', methods=['GET'])
def echo():
    """DICOM C-ECHO - test połączenia"""
    return jsonify({
        "status": "success",
        "message": "DICOM C-ECHO successful",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🏥 Symulator serwera DICOM uruchomiony")
    print("📡 Nasłuchuje na porcie 104 (standardowy port DICOM)")
    print("🔍 Uruchom skaner WiFi aby wykryć ten serwer")
    
    # Uruchom na porcie 104 (standardowy port DICOM)
    app.run(host='0.0.0.0', port=104, debug=False)
```

**Uruchom symulator:**
```bash
# Na Raspberry Pi
python3 simulator_dicom.py
```

---

### 3.5. Symulacja Serwera HL7 na Raspberry Pi

**Utwórz plik `simulator_hl7.py`:**

```python
#!/usr/bin/env python3
"""
Symulator serwera HL7 na Raspberry Pi
Port 5000 - często używany dla HL7
"""

from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.route('/hl7', methods=['POST'])
def receive_hl7():
    """Odbierz wiadomość HL7"""
    hl7_message = request.data.decode('utf-8')
    print(f"Otrzymano wiadomość HL7: {hl7_message}")
    return "ACK", 200

@app.route('/hl7/patient', methods=['GET'])
def get_patient_hl7():
    """Zwróć dane pacjenta w formacie HL7"""
    # Przykładowa wiadomość HL7 ADT^A01 (Admit Patient)
    hl7_message = (
        "MSH|^~\\&|HIS|HOSPITAL|LAB|20260118120000||ADT^A01|12345|P|2.5\r"
        "PID|1||123456||KOWALSKI^JAN||19800101|M|||123 Main St|||555-1234\r"
        "PV1|1|I|ICU^101^A|||123456^DR. SMITH|||||||||||V123456789\r"
    )
    return hl7_message, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    print("🏥 Symulator serwera HL7 uruchomiony")
    print("📡 Nasłuchuje na porcie 5000")
    print("🔍 Uruchom skaner WiFi aby wykryć ten serwer")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**Uruchom symulator:**
```bash
# Na Raspberry Pi
python3 simulator_hl7.py
```

---

## 🔍 Krok 4: Testowanie Skanerem

### 4.1. Test BLE (ESP32)

**Na komputerze/laptopie:**
```bash
# Aktywuj venv
source venv/bin/activate

# Uruchom skaner BLE
python src/scanner.py --ble
```

**Powinieneś zobaczyć:**
```
✓ Wykryto: Glukometr-Symulator (XX:XX:XX:XX:XX:XX)
🔒 Analizuję właściwości bezpieczeństwa urządzeń...
```

---

### 4.2. Test WiFi (Raspberry Pi)

**Upewnij się, że:**
- Raspberry Pi jest w tej samej sieci WiFi co komputer
- Symulator DICOM/HL7 jest uruchomiony na Raspberry Pi

**Na komputerze/laptopie:**
```bash
# Uruchom skaner WiFi
python src/scanner.py --wifi
```

**Powinieneś zobaczyć:**
```
✓ Wykryto: 192.168.1.XXX (Raspberry Pi)
  Porty: 104 (DICOM), 5000 (HL7)
```

---

### 4.3. Test Wszystkich Protokołów

```bash
# Uruchom pełny skan
python src/scanner.py --ble --wifi
```

---

## 📚 Krok 5: Rozszerzanie Symulacji

### 5.1. Więcej Urządzeń BLE na ESP32

Możesz zaprogramować ESP32 jako:
- **Pulsoksymetr** (Heart Rate Service - UUID 0x180D)
- **Ciśnieniomierz** (Blood Pressure Service - UUID 0x1810)
- **Opaska fitness** (Fitness Service)

**Przykład: Pulsoksymetr**
```cpp
// Zmień UUID:
#define SERVICE_UUID        "180D"  // Heart Rate Service
#define CHARACTERISTIC_UUID "2A37"  // Heart Rate Measurement

// W loop():
int heartRate = random(60, 100); // 60-100 bpm
```

---

### 5.2. Więcej Serwisów na Raspberry Pi

Możesz dodać:
- **Serwer PACS** (Picture Archiving and Communication System)
- **Serwer EMR** (Electronic Medical Records)
- **Serwer IoT** (urządzenia medyczne IoT)

---

## 🎯 Krok 6: Pierwszy Profesjonalny Test

### 6.1. Pełny Audyt Bezpieczeństwa

```bash
# Uruchom pełny audyt
python src/scanner.py --ble --wifi --audit
```

**Co to robi:**
- ✅ Skanuje wszystkie protokoły
- ✅ Analizuje bezpieczeństwo
- ✅ Testuje podatności
- ✅ Generuje raporty (JSON, CSV, PDF)

---

### 6.2. Monitorowanie Ciągłe

```bash
# Monitoruj urządzenia co 60 sekund
python src/scanner.py --monitor
```

---

## 🐛 Rozwiązywanie Problemów

### Problem: ESP32 nie jest widoczny w skanerze

**Rozwiązanie:**
1. Sprawdź czy ESP32 jest włączony (LED powinien migać)
2. Sprawdź Serial Monitor - czy widzisz "Symulator gotowy!"
3. Upewnij się, że Bluetooth jest włączony na komputerze
4. Spróbuj zrestartować ESP32 (odłącz i podłącz USB)

---

### Problem: Raspberry Pi nie jest widoczny w skanerze WiFi

**Rozwiązanie:**
1. Sprawdź czy Raspberry Pi jest w tej samej sieci WiFi
2. Sprawdź czy serwery są uruchomione:
   ```bash
   # Na Raspberry Pi
   netstat -tuln | grep -E "104|5000"
   ```
3. Sprawdź firewall:
   ```bash
   # Na Raspberry Pi
   sudo ufw allow 104
   sudo ufw allow 5000
   ```

---

### Problem: Błędy podczas instalacji

**Rozwiązanie:**
1. Upewnij się, że masz najnowszą wersję Python (3.8+)
2. Zaktualizuj pip:
   ```bash
   pip install --upgrade pip
   ```
3. Zainstaluj zależności ponownie:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📊 Podsumowanie - Co Masz Teraz

### ✅ Sprzęt:
- ESP32 - symuluje urządzenia BLE
- Raspberry Pi - symuluje serwery medyczne
- Czytnik NFC (opcjonalnie) - do skanowania NFC

### ✅ Umiejętności:
- Programowanie ESP32 jako symulator urządzeń medycznych
- Konfiguracja Raspberry Pi jako serwer medyczny
- Testowanie skanerem
- Audyt bezpieczeństwa

### ✅ Następne Kroki:
1. Rozszerz symulację (więcej urządzeń)
2. Dodaj prawdziwe urządzenia (gdy możesz)
3. Uzyskaj certyfikaty (CEH, CISSP)
4. Zacznij oferować usługi audytu

---

## 🎓 Materiały do Nauki

### ESP32:
- Dokumentacja: https://docs.espressif.com/projects/esp-idf/
- Przykłady BLE: https://github.com/espressif/esp-idf/tree/master/examples/bluetooth

### Raspberry Pi:
- Oficjalna dokumentacja: https://www.raspberrypi.org/documentation/
- Flask (serwery): https://flask.palletsprojects.com/

### Bluetooth BLE:
- Specyfikacja medyczna: https://www.bluetooth.com/specifications/specs/
- UUID serwisów medycznych: https://www.bluetooth.com/specifications/assigned-numbers/

---

**Powodzenia w nauce! 🚀**

Jeśli masz pytania, sprawdź dokumentację w projekcie lub zapytaj w Issues na GitHub.
