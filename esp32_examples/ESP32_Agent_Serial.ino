/*
 * ESP32 Agent Serial - wysyła wyniki skanów BLE do Raspberry Pi przez USB/UART
 *
 * Użycie: podłącz ESP32 do Raspberry Pi kablem USB. Na Pi uruchom:
 *   python scripts/esp32_serial_reader.py
 *
 * ESP32 skanuje BLE co kilka sekund i wysyła każdy wynik jako jedną linię JSON
 * do portu szeregowego. Pi może te dane zapisywać, wyświetlać lub przekazywać
 * do skanera/dashboardu.
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

    // Jedna linia JSON na urządzenie (łatwe do parsowania na Pi)
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
