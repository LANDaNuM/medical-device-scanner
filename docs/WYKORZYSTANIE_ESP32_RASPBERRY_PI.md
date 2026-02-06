++# 🔌 Wykorzystanie ESP32 i Raspberry Pi 5 w Projekcie

> **Nie wiesz, jak to fizycznie podłączyć (komputer ↔ Pi ↔ ESP32)?**  
> **Raspberry Pi bez ekranu? Programator do ESP32?**  
> → Zobacz ** [PODLACZENIE_OD_ZERA.md](PODLACZENIE_OD_ZERA.md) ** – tam jest to krok po kroku dla początkujących.

---

## 📦 Masz do dyspozycji:
- ✅ **ESP-WROOM-32 ESP32** (USB-C CH340, WiFi, Bluetooth, 4MB Flash)
- ✅ **Raspberry Pi 5** (8GB RAM, 128GB Storage)

---

## 🎯 Propozycje Wykorzystania

### 1. 🍓 Raspberry Pi 5 jako Główny Serwer Skanera (ZALECANE)

**Co możesz zrobić:**
- Uruchomić cały projekt skanera na Raspberry Pi 5
- Używać jako serwer 24/7 do monitorowania urządzeń medycznych
- Hostować API i Dashboard (Streamlit)
- Przechowywać historię skanowań

**Zalety:**
- ✅ Niski pobór mocy (można zostawić włączone 24/7)
- ✅ Wystarczająca wydajność (8GB RAM, szybki procesor)
- ✅ Wbudowany WiFi i Bluetooth (wszystkie protokoły działają)
- ✅ Dużo miejsca na dane (128GB)

**Instalacja:**
```bash
# 1. Zainstaluj Raspberry Pi OS na karcie SD
# 2. Połącz się przez SSH lub bezpośrednio

# 3. Zainstaluj Python i zależności
sudo apt-get update
sudo apt-get install python3-pip python3-venv git nmap

# 4. Sklonuj projekt
git clone <repo-url>
cd medical-device-scanner-main

# 5. Utwórz virtual environment
python3 -m venv venv
source venv/bin/activate

# 6. Zainstaluj zależności
pip install -r requirements.txt

# 7. Uruchom skaner
python src/scanner.py --ble --wifi

# 8. Uruchom dashboard (opcjonalnie)
streamlit run src/dashboard.py
```

**Użycie:**
- Monitorowanie ciągłe: `python src/monitor.py`
- Skanowanie jednorazowe: `python src/scanner.py`
- API serwer: `python src/api_server.py`

---

### 2. 📡 ESP32 jako Urządzenie Testowe (Emulacja Urządzenia Medycznego)

**Co możesz zrobić:**
- Programować ESP32 jako symulowane urządzenie medyczne (glukometr, pulsoksymetr)
- Testować skaner na prawdziwym urządzeniu BLE/WiFi
- Symulować różne scenariusze bezpieczeństwa (z szyfrowaniem, bez szyfrowania)
- Testować wykrywanie podatności

**Zalety:**
- ✅ Prawdziwe urządzenie do testowania skanera
- ✅ Możesz symulować różne typy urządzeń medycznych
- ✅ Testowanie w rzeczywistych warunkach
- ✅ Niskie koszty (ESP32 ~50 PLN)

**Przykładowe projekty ESP32:**

#### A) ESP32 jako Glukometr BLE
```cpp
// ESP32_Glukometr_BLE.ino
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// UUID dla Glucose Service (standard medyczny)
#define GLUCOSE_SERVICE_UUID "00001808-0000-1000-8000-00805f9b34fb"
#define GLUCOSE_MEASUREMENT_UUID "00002a18-0000-1000-8000-00805f9b34fb"

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;

void setup() {
  Serial.begin(115200);
  
  // Inicjalizuj BLE
  BLEDevice::init("GlucoSmart_Test");
  pServer = BLEDevice::createServer();
  
  BLEService* pService = pServer->createService(GLUCOSE_SERVICE_UUID);
  
  // Characteristic dla pomiaru glukozy
  pCharacteristic = pService->createCharacteristic(
    GLUCOSE_MEASUREMENT_UUID,
    BLECharacteristic::PROPERTY_READ | 
    BLECharacteristic::PROPERTY_NOTIFY
  );
  
  pService->start();
  
  // Rozpocznij advertising
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(GLUCOSE_SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  BLEDevice::startAdvertising();
  
  Serial.println("Glukometr BLE uruchomiony!");
}

void loop() {
  // Symuluj pomiar glukozy (co 5 sekund)
  float glucose = random(70, 120); // 70-120 mg/dL
  
  // Wyślij dane przez BLE
  pCharacteristic->setValue(glucose);
  pCharacteristic->notify();
  
  Serial.printf("Wysłano pomiar: %.1f mg/dL\n", glucose);
  delay(5000);
}
```

#### B) ESP32 jako Urządzenie WiFi (Serwer HTTP)
```cpp
// ESP32_WiFi_Device.ino
#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "Twoja_Siec";
const char* password = "Twoje_Haslo";

WebServer server(80);

void setup() {
  Serial.begin(115200);
  
  // Połącz z WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nPołączono z WiFi!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  
  // Endpoint dla danych medycznych
  server.on("/api/vitals", []() {
    String json = "{"
      "\"heart_rate\":" + String(random(60, 100)) + ","
      "\"spo2\":" + String(random(95, 100)) + ","
      "\"temperature\":" + String(36.5 + random(0, 10)/10.0) +
    "}";
    server.send(200, "application/json", json);
  });
  
  server.begin();
  Serial.println("Serwer HTTP uruchomiony!");
}

void loop() {
  server.handleClient();
}
```

**Jak użyć:**
1. Wgraj kod na ESP32 przez Arduino IDE
2. Uruchom skaner na Raspberry Pi: `python src/scanner.py --ble --wifi`
3. ESP32 zostanie wykryte jako urządzenie medyczne

---

### 3. 🔍 ESP32 jako Dodatkowy Agent Skanujący (Zaawansowane)

**Co możesz zrobić:**
- ESP32 skanuje urządzenia BLE w swoim zasięgu
- Wysyła wyniki do Raspberry Pi przez WiFi
- Rozszerza zasięg skanowania (distributed scanning)
- Zbiera dane z różnych lokalizacji

**Architektura:**
```
ESP32 (Agent) → WiFi → Raspberry Pi 5 (Centralny Serwer)
     ↓
  Skanuje BLE
  lokalnie
```

**Kod ESP32 (Agent):**
```cpp
// ESP32_Agent.ino
#include <WiFi.h>
#include <HTTPClient.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>

const char* ssid = "Twoja_Siec";
const char* password = "Twoje_Haslo";
const char* serverURL = "http://192.168.1.100:5000/api/devices"; // IP Raspberry Pi

BLEScan* pBLEScan;

void setup() {
  Serial.begin(115200);
  
  // Połącz z WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nPołączono z WiFi!");
  
  // Inicjalizuj BLE
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);
}

void loop() {
  // Skanuj BLE przez 5 sekund
  BLEScanResults foundDevices = pBLEScan->start(5, false);
  
  // Wyślij wyniki do Raspberry Pi
  for (int i = 0; i < foundDevices.getCount(); i++) {
    BLEAdvertisedDevice device = foundDevices.getDevice(i);
    
    // Przygotuj JSON
    String json = "{"
      "\"mac_address\":\"" + String(device.getAddress().toString().c_str()) + "\","
      "\"name\":\"" + String(device.getName().c_str()) + "\","
      "\"rssi\":" + String(device.getRSSI()) + ","
      "\"protocol\":\"BLE\""
    "}";
    
    // Wyślij do serwera
    sendToServer(json);
  }
  
  pBLEScan->clearResults();
  delay(10000); // Skanuj co 10 sekund
}

void sendToServer(String json) {
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(json);
  if (httpResponseCode > 0) {
    Serial.printf("Wysłano: %d\n", httpResponseCode);
  } else {
    Serial.printf("Błąd: %d\n", httpResponseCode);
  }
  
  http.end();
}
```

**Kod Python na Raspberry Pi (Endpoint API):**
```python
# Dodaj do src/api_server.py
@app.route('/api/devices', methods=['POST'])
def receive_device_from_agent():
    """Odbiera dane z agenta ESP32"""
    data = request.json
    # Zapisz urządzenie do bazy danych
    # ...
    return {"status": "ok"}
```

---

### 4. 🧪 ESP32 jako Urządzenie do Testowania Podatności

**Co możesz zrobić:**
- Symulować urządzenie z podatnościami bezpieczeństwa
- Testować wykrywanie podatności przez skaner
- Symulować różne scenariusze ataków

**Przykłady podatności do symulacji:**
1. **Brak szyfrowania** - otwarte połączenie BLE
2. **Brak autoryzacji** - każdy może się połączyć
3. **Słabe hasło WiFi** - łatwe do złamania
4. **Otwarte porty** - HTTP bez HTTPS
5. **Brak aktualizacji** - stara wersja firmware

**Kod ESP32 (Podatne urządzenie):**
```cpp
// ESP32_Vulnerable_Device.ino
#include <BLEDevice.h>
#include <BLEServer.h>

BLEServer* pServer = NULL;

void setup() {
  Serial.begin(115200);
  
  // Inicjalizuj BLE BEZ szyfrowania
  BLEDevice::init("Vulnerable_Device");
  pServer = BLEDevice::createServer();
  
  // Utwórz service BEZ wymagania parowania
  BLEService* pService = pServer->createService("12345678-1234-1234-1234-123456789abc");
  
  // Characteristic BEZ autoryzacji
  BLECharacteristic* pChar = pService->createCharacteristic(
    "87654321-4321-4321-4321-cba987654321",
    BLECharacteristic::PROPERTY_READ | 
    BLECharacteristic::PROPERTY_WRITE
  );
  
  // BEZ szyfrowania - każdy może odczytać/zapisać
  pChar->setValue("Sensitive_Medical_Data");
  
  pService->start();
  
  // Rozpocznij advertising
  BLEDevice::startAdvertising();
  
  Serial.println("PODATNE urządzenie uruchomione (celowo!)");
}

void loop() {
  delay(1000);
}
```

**Testowanie:**
1. Wgraj kod na ESP32
2. Uruchom skaner: `python src/scanner.py --ble`
3. Skaner powinien wykryć podatności:
   - ❌ Brak szyfrowania
   - ❌ Brak autoryzacji
   - ⚠️ Security Score: ~50/100

---

### 5. 📊 Raspberry Pi 5 jako Serwer Dashboard + API

**Co możesz zrobić:**
- Hostować Streamlit Dashboard
- Uruchomić REST API
- Przechowywać historię skanowań
- Eksportować dane do SIEM

**Uruchomienie Dashboard:**
```bash
# Na Raspberry Pi
cd medical-device-scanner-main
source venv/bin/activate

# Uruchom dashboard
streamlit run src/dashboard.py --server.port 8501 --server.address 0.0.0.0

# Dostęp z przeglądarki:
# http://192.168.1.100:8501 (zamień na IP Twojego Pi)
```

**Uruchomienie API:**
```bash
# Uruchom API serwer
python src/api_server.py

# API będzie dostępne na:
# http://192.168.1.100:5000
```

**Dostęp z innych urządzeń:**
- Laptop: `http://192.168.1.100:8501` (dashboard)
- Telefon: `http://192.168.1.100:8501` (dashboard mobilny)
- ESP32: `http://192.168.1.100:5000/api/...` (API)

---

### 6. 🔗 Bezpośrednie podłączenie Raspberry Pi ↔ ESP32 (współpraca obu urządzeń)

**Tak, da się – i można wykorzystać oba urządzenia jednocześnie.** Masz dwie główne opcje połączenia fizycznego.

#### Opcja A: Kabel USB (najprostsza)

- **Podłączenie:** Kabel USB (USB-A na Pi, USB-C lub micro-USB na ESP32) z Raspberry Pi do ESP32.
- **Efekt:** Na Pi pojawi się port szeregowy, np. `/dev/ttyUSB0` (CH340) lub `/dev/ttyACM0`. Raspberry Pi „widzi” ESP32 jak drugi komputer przez port szeregowy.
- **Zalety:** Jedna wtyczka, zasilanie ESP32 z Pi, brak lutowania. Idealne na start.

**Na Raspberry Pi:**
```bash
# Sprawdź, czy Pi widzi ESP32
ls /dev/ttyUSB* /dev/ttyACM*

# Zainstaluj obsługę portu szeregowego (jeśli brak)
sudo usermod -aG dialout $USER   # wyloguj się i zaloguj potem
pip install pyserial
```

**Współpraca:** Na ESP32 wgrywasz program, który np. skanuje BLE i wysyła wyniki do Serial (np. linie JSON). Na Pi uruchamiasz skrypt Pythona, który czyta z `/dev/ttyUSB0` (lub `ttyACM0`) i np. zapisuje do pliku, wysyła do API skanera albo wyświetla w konsoli. Pi w tym czasie może normalnie działać jako serwer skanera (WiFi/BLE z Pi, dodatkowe dane z ESP32 przez USB).

**Gotowy przykład w projekcie:**
- **ESP32:** wgraj `esp32_examples/ESP32_Unified_Scanner` – skanuje BLE i WiFi, wysyła **tylko zmiany** (event: `new` / `gone`) + co ~60 s `heartbeat`. Dzięki temu sens ma działanie 24/7 – nie zalewasz logów tym samym.
- **Raspberry Pi:** `python scripts/esp32_serial_reader.py --out wyniki_esp32.json --enrich`. Wymaga: `pip install pyserial`.

**Zaplanowane skanowanie (np. jutro 8:00) i raport:**  
Żeby **zaplanować skan przez ESP32** (np. jutro o 8:00) i **dostać raport** (plik + opcjonalnie email), użyj na Pi flag `--duration N` (skan N sekund, potem zapis raportu) i `--report-email ADR`. Jednorazowo: `at 08:00 tomorrow` z poleceniem uruchamiającym czytnik z `--duration 300 --out raport.json --report-email twoj@email.com`. Codziennie o 8:00: wpis w **cron** (`0 8 * * *`). Pełny opis i przykłady: **[FLAGI.md – sekcja Mikrokontroler (ESP32) i „Zaplanowane skanowanie ESP32”](FLAGI.md#-mikrokontroler-esp32)**.

#### Opcja B: UART przez GPIO (bez USB)

- **Podłączenie (3.3 V – nie łączyć z 5 V):**

| Raspberry Pi (GPIO) | ESP32        |
|--------------------|--------------|
| GPIO 14 (Tx)       | RX (np. GPIO 16) |
| GPIO 15 (Rx)       | TX (np. GPIO 17) |
| GND                | GND          |

- **Uwaga:** Na Pi trzeba wyłączyć konsolę szeregową, żeby GPIO 14/15 nie były zajęte przez login. W `raspi-config`: Interface Options → Serial Port → „No” na login shell, „Yes” na hardware serial. Potem port to zwykle `/dev/serial0` lub `/dev/ttyAMA0`.
- **Zalety:** Nie zajmujesz portu USB na Pi, możesz mieć ESP32 na stałe przy Pi w jednej obudowie.

**Współpraca (A i B):**  
- **ESP32:** np. skan BLE co X sekund → wynik w jednej linii (np. JSON) → `Serial.println(...)`. Albo odbieranie komend z Pi (np. „START”, „STOP”) i wykonywanie skanów na żądanie.  
- **Raspberry Pi:** skrypt Python (`serial.Serial("/dev/ttyUSB0", 115200)`) czyta linie, parsuje JSON i np. dopisuje urządzenia do bazy, wywołuje API skanera albo pokazuje na dashboardzie. Jednocześnie Pi może sam skanować WiFi/BLE – wtedy masz **dwa źródła danych**: skaner na Pi + agent na ESP32 (przez USB lub UART).

**Podsumowanie:**  
- **Chcesz szybko zacząć:** podłącz ESP32 do Pi **kablem USB**, wgraj na ESP32 program wysyłający dane przez Serial, na Pi napisz krótki skrypt w Pythonie (pyserial) odbierający te dane i łączący je z resztą skanera (np. zapis do pliku/API).  
- **Chcesz zostawić USB wolne:** użyj **UART po GPIO** (Tx/Rx/GND) i tego samego protokołu (linie tekstu/JSON po Serial).  
W obu przypadkach oba urządzenia współpracują: Pi = główny mózg (skaner, dashboard, API), ESP32 = dodatkowy agent (np. BLE w innym miejscu, czujniki, testy) wysyłający dane do Pi.

---

## 🎯 Rekomendowany Plan Wdrożenia

### Krok 1: Setup Raspberry Pi 5 (Główny Serwer)
1. ✅ Zainstaluj Raspberry Pi OS
2. ✅ Sklonuj projekt i zainstaluj zależności
3. ✅ Przetestuj skanowanie: `python src/scanner.py --ble --wifi`
4. ✅ Uruchom dashboard: `streamlit run src/dashboard.py`

### Krok 2: Setup ESP32 (Urządzenie Testowe)
1. ✅ Zainstaluj Arduino IDE
2. ✅ Dodaj ESP32 board support
3. ✅ Wgraj kod glukometru BLE (przykład powyżej)
4. ✅ Przetestuj wykrywanie przez skaner na Pi

### Krok 3: Integracja
1. ✅ Uruchom skaner na Pi: `python src/scanner.py --ble`
2. ✅ Sprawdź czy ESP32 jest wykrywane
3. ✅ Sprawdź dashboard: czy urządzenie się pojawia
4. ✅ Przetestuj różne scenariusze (z/bez szyfrowania)

### Krok 4: Zaawansowane (Opcjonalnie)
1. ✅ Dodaj ESP32 jako agent (distributed scanning)
2. ✅ Symuluj podatności na ESP32
3. ✅ Testuj wykrywanie anomalii

---

## 🔄 Aktualizacja firmware ESP32 bez podłączania do PC

Żeby wgrać nowy plik .ino, ESP32 **musi** być podłączone do czegoś przez USB (PC albo Raspberry Pi). Możesz jednak **nie podłączać go do komputera** – wystarczy, że na stałe stoi przy Raspberry Pi.

### Opcja A: Wgrywanie z Raspberry Pi (ESP32 zawsze przy Pi)

**Idea:** ESP32 jest podłączone do Pi przez USB. Edytujesz kod na PC, ale **wgrywasz z Pi** – nie przenosisz ESP32 do komputera.

1. **Na Raspberry Pi** (przez SSH):
   - Zainstaluj Arduino CLI lub esptool (do wgrywania plików .bin).
   - Projekt trzymaj na Pi (np. `git pull` z Twojego repo po zmianach na PC).

2. **Sposób 1 – kompilacja na PC, wgrywanie z Pi:**
   - Na **PC:** w Arduino IDE otwierasz `.ino`, robisz **Sketch → Export compiled Binary**. Powstaje plik `.bin` w folderze szkicu.
   - Kopiujesz ten plik na Pi (np. `scp`, pendrive, albo `git push` z PC → `git pull` na Pi, jeśli .bin trzymasz w repo lub jako artefakt).
   - Na **Pi:** wgrywasz:  
     `esptool.py --port /dev/ttyUSB0 write_flash 0x10000 ścieżka/do/pliku.bin`  
     (adres `0x10000` jest typowy dla Arduino ESP32; jeśli używasz innego schematu partycji, sprawdź w Arduino IDE w logu przy Upload).

3. **Sposób 2 – kompilacja i wgrywanie na Pi:**
   - Na Pi instalujesz **Arduino CLI** (headless, bez GUI).  
     Następnie: `arduino-cli core install esp32:esp32`, `arduino-cli compile ...`, `arduino-cli upload -p /dev/ttyUSB0 ...`.  
   - Kod edytujesz na PC i synchronizujesz na Pi (git, rsync, itd.). Na Pi tylko kompilujesz i wgrywasz.

**Efekt:** ESP32 nie musi być nigdy podłączone do PC – tylko do Pi. Aktualizujesz projekt na PC, a „flashowanie” robisz z Pi.

### Opcja B: Aktualizacja OTA (przez WiFi)

Po **pierwszym** wgraniu (przez USB) możesz zrobić tak, żeby kolejne aktualizacje szły **przez WiFi** – bez kabla.

- Wymaga: schematu partycji **z OTA** (np. „Minimal SPIFFS (1.9MB APP with OTA)”).
- W kodzie ESP32: obsługa OTA (np. `ArduinoOTA` w pętli) + ESP32 w sieci WiFi.
- Na PC lub Pi: narzędzie do wysłania pliku `.bin` na ESP32 (np. skrypt Pythona z `requests` do endpointu OTA na ESP32).

To daje wygodę „bez kabla”, ale wymaga więcej konfiguracji (OTA w szkicu, stały adres IP lub mDNS, skrypt do wysyłki). Jeśli ESP32 i tak stoi przy Pi i masz dostęp do USB, **Opcja A** zwykle wystarczy.

### Podsumowanie

| Sytuacja | Co zrobić |
|----------|-----------|
| Masz PC i Pi; ESP32 przy Pi | Edytuj na PC → kompiluj na PC → kopiuj .bin na Pi → wgrywaj z Pi (`esptool`). Albo: edytuj na PC, sync na Pi, kompiluj i wgrywaj Arduino CLI na Pi. |
| Chcesz zero kabla po pierwszym flashu | Użyj OTA: pierwsze wgranie przez USB, potem aktualizacje przez WiFi. |
| Jednorazowa zmiana .ino | Podłącz ESP32 do PC, Upload w Arduino IDE – najszybciej. |

Dzięki temu możesz **aktualizować projekt (i firmware)** bez konieczności podłączania ESP32 do komputera – wystarczy Pi i USB między Pi a ESP32.

---

## 📚 Przydatne Linki i Dokumentacja

### ESP32:
- **Arduino IDE Setup:** https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html
- **BLE Examples:** https://github.com/espressif/arduino-esp32/tree/master/libraries/BLE/examples
- **WiFi Examples:** https://github.com/espressif/arduino-esp32/tree/master/libraries/WiFi/examples

### Raspberry Pi 5:
- **Raspberry Pi OS:** https://www.raspberrypi.com/software/
- **SSH Setup:** https://www.raspberrypi.com/documentation/computers/remote-access.html
- **Python Setup:** `sudo apt-get install python3-pip python3-venv`

### Projekt:
- **Dokumentacja:** `/docs/` folder
- **Przewodnik Python:** `/docs/PRZEWODNIK_PYTHON_CZESC_1.md`
- **Jak uruchomić:** `/docs/JAK_URUCHOMIC.md`

---

## 📊 Wartość wyników ESP32 i co można dodać

### Co ESP32 robi teraz (ESP32_Unified_Scanner)

- **Tylko zmiany** – wysyła dane **gdy coś się zmieni**: `event: "new"` (nowe urządzenie BLE / nowa sieć WiFi) lub `event: "gone"` (urządzenie/sieć zniknęła). Dzięki temu sens ma działanie 24/7 – nie zalewasz logów tym samym, tylko dostajesz zdarzenia przy zmianach.
- **Heartbeat** – co ~60 s wysyła `type: "heartbeat"` z liczbą urządzeń BLE i WiFi (żeby wiadomo, że skaner żyje).
- **Pola:** `type`, `mac`, `name`, `rssi`, `service_uuid`, `manufacturer_data` (BLE), `ssid`, `channel` (WiFi). Po stronie Pi skrypt `--enrich` dodaje producenta (OUI), typ urządzenia, podpowiedzi podatności.

**Czy z tego wynika, że urządzenia są podatne?** Sam ESP32 **nie** robi pełnego audytu (skan portów, CVE, szyfrowanie). Pokazuje tylko **kto jest w zasięgu** i **kiedy się pojawia/znika**. Wartość: ciągły monitoring „co się zmienia” + sygnał do dalszej analizy na Pi.

### Gdzie sprawdzać podatności

- **Pełny audyt (podatności, porty, CVE)** – na **Raspberry Pi** uruchom główny skaner:  
  `python src/scanner.py --ble --wifi --audit`  
  To on łączy się z urządzeniami, skanuje porty, ocenia szyfrowanie i zwraca „podatny / nie”.
- **Rola ESP32:** wykrywa **nowe** urządzenia (event `new`); na Pi możesz wtedy ręcznie lub skryptem uruchomić pełny skan na tym MAC/SSID.

### Co można dodać w przyszłości

| Pomysł | Opis |
|--------|------|
| **Test BLE „bez parowania”** | Na ESP32: próba połączenia BLE z urządzeniem; jeśli uda się **bez parowania** – wysłanie `ble_no_auth: true`. Daje konkretną podpowiedź „może być podatne”. Wymaga kodu BLE client na ESP32 (connect + disconnect). |
| **Pi uruchamia skan przy `new`** | Gdy `esp32_serial_reader.py` dostanie `event: "new"` (np. nowy MAC BLE), skrypt mógłby wywołać `scanner.py --ble` lub konkretny test na ten adres – wtedy ESP32 = „czujnik”, Pi = „audyt na żądanie”. |
| **Alerty** | Zapis `new`/`gone` do pliku lub bazy; przy `new` wysłanie maila/Slacka lub wpis do Splunk – „nowe urządzenie w zasięgu”. |

**Podsumowanie:** ESP32 ma sens jako **monitor zmian** (kto się pojawił/zniknął). Sam w sobie nie mówi „podatne / nie” – to robi główny skaner na Pi. Połączenie: ESP32 = ciągły monitoring, Pi = pełny audyt gdy trzeba.

---

## 💡 Pomysły na Rozszerzenie

### 1. **Sieć ESP32 Agentów**
- Wiele ESP32 skanujących w różnych lokalizacjach
- Centralny serwer na Raspberry Pi zbiera wszystkie dane
- Mapa urządzeń medycznych w całym budynku

### 2. **ESP32 jako Sensor**
- ESP32 z czujnikami (temperatura, wilgotność)
- Wysyła dane przez BLE jako urządzenie medyczne
- Testowanie wykrywania różnych typów urządzeń

### 3. **Raspberry Pi jako Gateway**
- Pi zbiera dane z wielu ESP32
- Przetwarza i analizuje
- Wysyła alerty (email, SMS) gdy wykryje podatności

### 4. **Machine Learning na Pi**
- Użyj Raspberry Pi 5 do trenowania modeli ML
- Wykrywanie anomalii w czasie rzeczywistym
- Przewidywanie ataków na podstawie wzorców

---

## ❓ FAQ

### Czy mogę używać ESP32 bez Raspberry Pi?
**TAK!** Możesz uruchomić skaner na laptopie i skanować ESP32. Raspberry Pi jest opcjonalny, ale przydatny do monitorowania 24/7.

### Czy potrzebuję programować ESP32?
**NIE!** Możesz używać tylko Raspberry Pi do skanowania istniejących urządzeń. ESP32 jest opcjonalny do testowania.

### Która opcja jest najlepsza dla początkujących?
**Opcja 1** (Raspberry Pi jako serwer) - najprostsza, nie wymaga programowania ESP32.

### Czy mogę używać wielu ESP32?
**TAK!** Możesz mieć wiele ESP32 jako agentów skanujących lub urządzenia testowe.

---

## 🎓 Podsumowanie

**Masz doskonały sprzęt do tego projektu!**

✅ **Raspberry Pi 5** - idealny jako główny serwer (wystarczająca wydajność, niski pobór mocy)
✅ **ESP32** - idealny do testowania i symulacji urządzeń medycznych

**Zalecany start:**
1. Uruchom projekt na Raspberry Pi 5
2. Przetestuj skanowanie istniejących urządzeń
3. (Opcjonalnie) Dodaj ESP32 jako urządzenie testowe

**Powodzenia! 🚀**
