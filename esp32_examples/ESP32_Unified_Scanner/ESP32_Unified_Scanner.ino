/*
 * ESP32 Unified Scanner - BLE + WiFi, changes only (new/gone) + BLE no-pairing test
 *
 * - Sends data ONLY when something changes: event:new / event:gone.
 * - For the first new BLE device in a cycle: attempt connection without pairing.
 *   If it succeeds, the line gets "ble_no_auth": true (possible vulnerability).
 * - Heartbeat every ~60 s.
 *
 * Connect to Pi via USB; on Pi: python scripts/esp32_serial_reader.py --out wyniki_esp32.json --enrich
 */

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEClient.h>
#include <WiFi.h>

#define BLE_SCAN_SEC      5
#define PAUSE_BETWEEN_MS  8000
#define MAX_BLE           25
#define MAX_WIFI          15

BLEScan* pBLEScan;
String lastBle[MAX_BLE];
String lastWifi[MAX_WIFI];
int nLastBle = 0;
int nLastWifi = 0;
int scanCount = 0;

bool inList(const String list[], int n, const String& key) {
  for (int i = 0; i < n; i++) {
    if (list[i].equals(key)) return true;
  }
  return false;
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("{\"agent\":\"ESP32-Unified\",\"mode\":\"changes_only\",\"status\":\"ready\"}");

  BLEDevice::init("ESP32-Scanner");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);
}

void loop() {
  scanCount++;

  // ---- Skan BLE ----
  BLEScanResults* bleResults = pBLEScan->start(BLE_SCAN_SEC, false);
  int curBle = 0;
  String curBleMacs[MAX_BLE];

  bool didConnectTest = false;
  for (int i = 0; i < bleResults->getCount() && curBle < MAX_BLE; i++) {
    BLEAdvertisedDevice dev = bleResults->getDevice(i);
    String name = dev.getName().length() ? dev.getName().c_str() : "(unknown)";
    String addr = dev.getAddress().toString().c_str();
    curBleMacs[curBle++] = addr;

    if (!inList(lastBle, nLastBle, addr)) {
      bool bleNoAuth = false;
      if (!didConnectTest) {
        BLEClient* pClient = BLEDevice::createClient();
        if (pClient->connect(dev.getAddress(), (uint32_t)2000)) {
          delay(200);
          if (pClient->isConnected()) bleNoAuth = true;
          pClient->disconnect();
          delay(100);
        }
        delete pClient;
        didConnectTest = true;
      }

      String serviceUuid;
      if (dev.haveServiceUUID()) serviceUuid = dev.getServiceUUID().toString().c_str();
      String mfgHex;
      if (dev.haveManufacturerData()) {
        String mfg = dev.getManufacturerData();
        for (unsigned int j = 0; j < (unsigned int)mfg.length() && j < 20; j++) {
          char h[4];
          snprintf(h, sizeof(h), "%02x", (unsigned char)mfg[j]);
          mfgHex += h;
        }
        if (mfg.length() > 20) mfgHex += "...";
      }
      char buf[560];
      int n = snprintf(buf, sizeof(buf),
                      "{\"type\":\"ble\",\"event\":\"new\",\"mac\":\"%s\",\"name\":\"%s\",\"rssi\":%d",
                      addr.c_str(), name.c_str(), dev.getRSSI());
      if (bleNoAuth) n += snprintf(buf + n, sizeof(buf) - n, ",\"ble_no_auth\":true");
      if (serviceUuid.length() > 0)
        n += snprintf(buf + n, sizeof(buf) - n, ",\"service_uuid\":\"%s\"", serviceUuid.c_str());
      if (mfgHex.length() > 0)
        n += snprintf(buf + n, sizeof(buf) - n, ",\"manufacturer_data\":\"%s\"", mfgHex.c_str());
      snprintf(buf + n, sizeof(buf) - n, "}");
      Serial.println(buf);
    }
  }

  for (int i = 0; i < nLastBle; i++) {
    if (!inList(curBleMacs, curBle, lastBle[i])) {
      Serial.print("{\"type\":\"ble\",\"event\":\"gone\",\"mac\":\"");
      Serial.print(lastBle[i]);
      Serial.println("\"}");
    }
  }

  for (int i = 0; i < curBle && i < MAX_BLE; i++) lastBle[i] = curBleMacs[i];
  nLastBle = curBle;
  pBLEScan->clearResults();

  delay(300);

  // ---- Skan WiFi ----
  int nw = WiFi.scanNetworks();
  int curWifi = 0;
  String curWifiSsids[MAX_WIFI];

  for (int i = 0; i < nw && curWifi < MAX_WIFI; i++) {
    String ssid = WiFi.SSID(i);
    if (ssid.length() == 0) continue;
    curWifiSsids[curWifi++] = ssid;
    if (!inList(lastWifi, nLastWifi, ssid)) {
      char buf[400];
      String bssidStr = WiFi.BSSIDstr(i);
      if (bssidStr.length() < 17) {
        const uint8_t* bssid = WiFi.BSSID(i);
        if (bssid) {
          char mac[18];
          snprintf(mac, sizeof(mac), "%02x:%02x:%02x:%02x:%02x:%02x",
                   bssid[0], bssid[1], bssid[2], bssid[3], bssid[4], bssid[5]);
          bssidStr = String(mac);
        }
      }
      if (bssidStr.length() >= 17) {
        snprintf(buf, sizeof(buf),
                 "{\"type\":\"wifi\",\"event\":\"new\",\"ssid\":\"%s\",\"bssid\":\"%s\",\"rssi\":%d,\"channel\":%d}",
                 ssid.c_str(), bssidStr.c_str(), WiFi.RSSI(i), WiFi.channel(i));
      } else {
        snprintf(buf, sizeof(buf),
                 "{\"type\":\"wifi\",\"event\":\"new\",\"ssid\":\"%s\",\"rssi\":%d,\"channel\":%d}",
                 ssid.c_str(), WiFi.RSSI(i), WiFi.channel(i));
      }
      Serial.println(buf);
    }
  }

  for (int i = 0; i < nLastWifi; i++) {
    if (!inList(curWifiSsids, curWifi, lastWifi[i])) {
      Serial.print("{\"type\":\"wifi\",\"event\":\"gone\",\"ssid\":\"");
      Serial.print(lastWifi[i]);
      Serial.println("\"}");
    }
  }

  for (int i = 0; i < curWifi && i < MAX_WIFI; i++) lastWifi[i] = curWifiSsids[i];
  nLastWifi = curWifi;
  WiFi.scanDelete();

  // Heartbeat every ~60 s (so the reader knows the scanner is alive)
  if (scanCount % 6 == 0) {
    Serial.print("{\"type\":\"heartbeat\",\"ble_count\":");
    Serial.print(nLastBle);
    Serial.print(",\"wifi_count\":");
    Serial.print(nLastWifi);
    Serial.println("}");
  }

  delay(PAUSE_BETWEEN_MS);
}
