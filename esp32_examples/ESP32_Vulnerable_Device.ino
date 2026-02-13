/*
 * ESP32 Vulnerable Device - Simulates a device with security vulnerabilities
 *
 * THIS CODE INTENTIONALLY CREATES SECURITY VULNERABILITIES!
 * Use ONLY for testing the security scanner.
 *
 * Vulnerabilities:
 * - No BLE encryption
 * - No authentication (anyone can connect)
 * - Medical data exposed
 * - No pairing required
 *
 * Requirements:
 * - ESP32 Board (ESP-WROOM-32)
 * - Arduino IDE with ESP32 board support
 *
 * Setup:
 * 1. Upload to ESP32
 * 2. Run scanner: python src/scanner.py --ble
 * 3. Scanner should detect the vulnerabilities!
 */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;

// UUID for test device (NOT standard medical UUID)
#define SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID  "87654321-4321-4321-4321-cba987654321"

// Connection callback (no authentication!)
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      Serial.println("⚠️ CONNECTION WITHOUT AUTHENTICATION!");
      Serial.println("   Anyone can connect - THIS IS A VULNERABILITY!");
    }

    void onDisconnect(BLEServer* pServer) {
      Serial.println("Disconnected");
    }
};

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== ⚠️ VULNERABLE BLE DEVICE ===");
  Serial.println("INTENTIONALLY CREATES SECURITY VULNERABILITIES!");
  Serial.println("Use ONLY for testing the scanner.\n");
  
  // Init BLE without encryption
  BLEDevice::init("Vulnerable_Medical_Device");
  pServer = BLEDevice::createServer();
  
  pServer->setCallbacks(new MyServerCallbacks());
  
  BLEService* pService = pServer->createService(SERVICE_UUID);
  
  // Characteristic without auth and without encryption (anyone can read/write)
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ |
    BLECharacteristic::PROPERTY_WRITE |
    BLECharacteristic::PROPERTY_NOTIFY
  );
  
  // Set sensitive medical data without encryption
  String sensitiveData = "Patient_ID:12345,Glucose:95,HeartRate:72";
  pCharacteristic->setValue(sensitiveData.c_str());
  
  pService->start();
  
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  BLEDevice::startAdvertising();
  
  Serial.println("❌ VULNERABILITIES:");
  Serial.println("   1. No BLE encryption");
  Serial.println("   2. No authentication (anyone can connect)");
  Serial.println("   3. Medical data accessible without password");
  Serial.println("   4. No pairing required");
  Serial.println("\n✅ Device advertising and ready for scanning!");
  Serial.println("   Run scanner: python src/scanner.py --ble");
}

void loop() {
  // Simulate sending data every 3 seconds (unencrypted!)
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 3000) {
    int glucose = random(70, 120);
    int heartRate = random(60, 100);
    
    String data = "Glucose:" + String(glucose) + ",HR:" + String(heartRate);
    
    pCharacteristic->setValue(data.c_str());
    pCharacteristic->notify();
    
    Serial.printf("📤 Sent data (unencrypted): %s\n", data.c_str());
    lastSend = millis();
  }
  
  delay(100);
}
