/*
 * ESP32 Agent Serial - sends BLE scan results to Raspberry Pi via USB/UART
 *
 * Usage: connect ESP32 to Raspberry Pi with USB cable. On Pi run:
 *   python scripts/esp32_serial_reader.py
 *
 * ESP32 scans BLE every few seconds and sends each result as one JSON line
 * on the serial port. Pi can save, display or forward data to scanner/dashboard.
 */

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>

#define SCAN_DURATION_SEC  5
#define SCAN_INTERVAL_MS   10000

BLEScan* pBLEScan;

void setup() {
  Serial.begin(115200);
  delay(500);

  BLEDevice::init("ESP32-Agent");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);

  Serial.println("{\"agent\":\"ESP32\",\"status\":\"ready\"}");
}

void loop() {
  BLEScanResults results = pBLEScan->start(SCAN_DURATION_SEC, false);

  for (int i = 0; i < results.getCount(); i++) {
    BLEAdvertisedDevice device = results.getDevice(i);
    String name = device.getName().length() ? device.getName().c_str() : "(unknown)";
    String addr = device.getAddress().toString().c_str();

    // One JSON line per device (easy to parse on Pi)
    Serial.print("{\"mac\":\"");
    Serial.print(addr);
    Serial.print("\",\"name\":\"");
    Serial.print(name);
    Serial.print("\",\"rssi\":");
    Serial.print(device.getRSSI());
    Serial.println(",\"protocol\":\"BLE\"}");
  }

  pBLEScan->clearResults();
  delay(SCAN_INTERVAL_MS);
}
