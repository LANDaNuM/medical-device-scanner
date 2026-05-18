# ESP32 examples for Medical Device Scanner

This folder contains Arduino example sketches for ESP32, used to test the medical device scanner.

## Available examples

### 1. `ESP32_Glukometr_BLE.ino`
Simulates a Bluetooth Low Energy glucose meter using the standard medical UUID (0x1808 – Glucose Service).

**Features:**
- Standard medical UUID (Glucose Service)
- Simulates glucose readings (70–120 mg/dL)
- Detected by the scanner as a medical device
- BLE notifications

**Usage:**
1. Upload the sketch to ESP32
2. Run scanner: `python src/scanner.py --ble`
3. ESP32 will be detected as a glucose meter

---

### 2. `ESP32_WiFi_Medical_Server.ino`
Runs an HTTP server on ESP32 that simulates a medical device with vital signs.

**Features:**
- HTTP server with vital data (heart rate, SpO2, temperature)
- API endpoints: `/api/vitals`, `/api/device/info`, `/api/health`
- Web interface (HTML)
- Detected by the WiFi scanner

**Usage:**
1. Set WiFi SSID and password in the code
2. Upload to ESP32
3. Check IP in Serial Monitor
4. Run scanner: `python src/scanner.py --wifi`
5. Open in browser: `http://<ESP32_IP>`

**Endpoints:**
- `GET /` – Web interface
- `GET /api/vitals` – Vital signs JSON
- `GET /api/device/info` – Device info
- `GET /api/health` – Device status

---

### 3. `ESP32_Unified_Scanner` – **single sketch: BLE + WiFi, multiple devices (recommended)**
One program instead of several – no need to re-flash different sketches. Scans **BLE** (phones, headphones, sensors, legacy devices) and **WiFi** networks (SSID and signal strength). Output goes over **Serial** (connect ESP32 to Pi via USB and on Pi run: `python scripts/esp32_serial_reader.py`). Optionally you can set WiFi and server address so data is also sent to Pi over the network.

---

### 4. `ESP32_Agent_Serial.ino` (BLE only, over USB)
Sends BLE scan results to Raspberry Pi over a USB cable (serial port). On Pi run: `python scripts/esp32_serial_reader.py`. Works with **direct** Pi ↔ ESP32 connection – no WiFi.

---

### 5. `ESP32_Vulnerable_Device.ino`
**⚠️ INTENTIONALLY CREATES SECURITY VULNERABILITIES!**

Simulates a device with vulnerabilities for testing scanner detection.

**Vulnerabilities:**
- No BLE encryption
- No authentication (anyone can connect)
- Medical data accessible without password
- No pairing required

**Usage:**
1. Upload to ESP32
2. Run scanner: `python src/scanner.py --ble`
3. Scanner should detect vulnerabilities (e.g. Security Score ~50/100, “No encryption”, “No authentication”)

---

## Installation and setup

**Requirements:**
- ESP32 board (e.g. ESP-WROOM-32)
- Arduino IDE
- USB cable (USB-C for ESP32)

### Step 1: Install ESP32 board support

1. Open Arduino IDE
2. Go to: **File** → **Preferences**
3. In “Additional Boards Manager URLs” add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to: **Tools** → **Board** → **Boards Manager**
5. Search for “ESP32” and install “esp32 by Espressif Systems”
6. Select board: **Tools** → **Board** → **ESP32 Arduino** → **ESP32 Dev Module**

### Step 2: Upload the sketch

1. Open the `.ino` file in Arduino IDE
2. Connect ESP32 via USB
3. Select port: **Tools** → **Port** → `<COM_PORT>` (Windows) or `/dev/ttyUSB0` (Linux)
4. Click **Upload** (right arrow)
5. Open Serial Monitor: **Tools** → **Serial Monitor** (115200 baud)

### Step 3: Test

1. Run the scanner on Raspberry Pi or laptop:
   ```bash
   python src/scanner.py --ble    # For BLE
   python src/scanner.py --wifi   # For WiFi
   ```
2. Check that ESP32 is detected
3. Optional: run dashboard: `streamlit run src/dashboard.py`

---

## Documentation

**ESP32 libraries:**
- **BLE:** Built into ESP32 Arduino Core
- **WiFi:** Built into ESP32 Arduino Core
- **WebServer:** Built into ESP32 Arduino Core

**Links:**
- [ESP32 Arduino Documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/)
- [BLE Examples](https://github.com/espressif/arduino-esp32/tree/master/libraries/BLE/examples)
- [WiFi Examples](https://github.com/espressif/arduino-esp32/tree/master/libraries/WiFi/examples)

---

## Troubleshooting

**ESP32 does not connect to WiFi**
- Check SSID and password in the code
- Ensure WiFi is 2.4 GHz (ESP32 does not support 5 GHz)
- Check distance from router

**BLE not detected**
- Ensure Bluetooth is on on the scanning device
- Check ESP32 Serial Monitor – is the device advertising?
- Try restarting ESP32

**Arduino IDE does not see ESP32**
- Install CH340 drivers (for USB-C adapters)
- Ensure the USB cable supports data (not only power)
- Try another USB port

---

## Security notice

**IMPORTANT:**
- The `ESP32_Vulnerable_Device.ino` example **intentionally** introduces vulnerabilities.
- **Do not use** this code in production.
- Use **only** for testing the security scanner.
- In real medical devices always use encryption and authentication.

---

These examples are part of the Medical Device Security Scanner project and are under the same license as the main project.
