/*
 * ESP32 Unified Scanner (Slim) - BLE + WiFi scan, tylko Serial
 *
 * Wersja bez HTTP/WiFi-connect, żeby zmieścić się w pamięci (1.3 MB).
 * - Skanuje BLE (telefony, czujniki, słuchawki itd.)
 * - Skanuje sieci WiFi (SSID + RSSI)
 * - Wyniki TYLKO przez Serial – podłącz do Pi USB, na Pi: python scripts/esp32_serial_reader.py
 *
 * Jeśli nadal "Sketch too big": w Arduino IDE ustaw
 *   Tools → Partition Scheme → "Huge APP (3MB No OTA)" lub "Minimal SPIFFS (1.9MB APP)"
 */

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <WiFi.h>

#define BLE_SCAN_SEC      5
#define PAUSE_BETWEEN_MS  8000

BLEScan* pBLEScan;

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("{\"agent\":\"ESP32-Unified\",\"mode\":\"serial\",\"status\":\"ready\"}");

  BLEDevice::init("ESP32-Scanner");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);
}

void loop() {
  // ---- Skan BLE (telefony, słuchawki, czujniki, stare urządzenia itd.) ----
  BLEScanResults* bleResults = pBLEScan->start(BLE_SCAN_SEC, false);

  for (int i = 0; i < bleResults->getCount(); i++) {
    BLEAdvertisedDevice dev = bleResults->getDevice(i);
    String name = dev.getName().length() ? dev.getName().c_str() : "(unknown)";
    String addr = dev.getAddress().toString().c_str();

    char buf[320];
    snprintf(buf, sizeof(buf),
             "{\"type\":\"ble\",\"mac\":\"%s\",\"name\":\"%s\",\"rssi\":%d}",
             addr.c_str(), name.c_str(), dev.getRSSI());
    Serial.println(buf);
  }
  pBLEScan->clearResults();

  delay(500);

  // ---- Skan sieci WiFi (SSID + RSSI) ----
  int n = WiFi.scanNetworks();
  for (int i = 0; i < n; i++) {
    char buf[320];
    String ssid = WiFi.SSID(i);
    int rssi = WiFi.RSSI(i);
    snprintf(buf, sizeof(buf),
             "{\"type\":\"wifi\",\"ssid\":\"%s\",\"rssi\":%d,\"channel\":%d}",
             ssid.c_str(), rssi, WiFi.channel(i));
    Serial.println(buf);
  }
  WiFi.scanDelete();

  delay(PAUSE_BETWEEN_MS);
}
