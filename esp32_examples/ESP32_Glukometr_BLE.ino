/*
 * ESP32 Glucose Meter BLE - Medical device simulation
 *
 * This code simulates a Bluetooth Low Energy (BLE) glucose meter
 * using the standard UUID for Glucose Service (0x1808).
 *
 * Requirements:
 * - ESP32 Board (ESP-WROOM-32)
 * - Arduino IDE with ESP32 board support
 * - ESP32 BLE Arduino library (built-in)
 *
 * Setup:
 * 1. Install ESP32 board support in Arduino IDE
 * 2. Upload this code to ESP32
 * 3. Run scanner on Raspberry Pi: python src/scanner.py --ble
 */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// UUID for Glucose Service (Bluetooth medical standard)
// 0x1808 = Glucose Service
#define GLUCOSE_SERVICE_UUID        "00001808-0000-1000-8000-00805f9b34fb"
// 0x2A18 = Glucose Measurement Characteristic
#define GLUCOSE_MEASUREMENT_UUID    "00002a18-0000-1000-8000-00805f9b34fb"
// 0x2A34 = Glucose Feature Characteristic
#define GLUCOSE_FEATURE_UUID        "00002a34-0000-1000-8000-00805f9b34fb"

BLEServer* pServer = NULL;
BLECharacteristic* pGlucoseMeasurement = NULL;
BLECharacteristic* pGlucoseFeature = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

// Connection/disconnection callbacks
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("Device connected");
    }

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("Device disconnected");
    }
};

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== ESP32 Glukometr BLE ===");
  
  BLEDevice::init("GlucoSmart_Pro");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  BLEService* pService = pServer->createService(GLUCOSE_SERVICE_UUID);
  
  // Glucose Measurement Characteristic
  pGlucoseMeasurement = pService->createCharacteristic(
    GLUCOSE_MEASUREMENT_UUID,
    BLECharacteristic::PROPERTY_READ |
    BLECharacteristic::PROPERTY_NOTIFY |
    BLECharacteristic::PROPERTY_INDICATE
  );
  
  // Glucose Feature Characteristic
  pGlucoseFeature = pService->createCharacteristic(
    GLUCOSE_FEATURE_UUID,
    BLECharacteristic::PROPERTY_READ
  );
  
  pGlucoseMeasurement->addDescriptor(new BLE2902());
  
  uint8_t featureValue[2] = {0x01, 0x00}; // Basic features
  pGlucoseFeature->setValue(featureValue, 2);
  
  pService->start();
  
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(GLUCOSE_SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  
  Serial.println("Glucose meter BLE started and advertising!");
  Serial.println("Name: GlucoSmart_Pro");
  Serial.println("Service UUID: 0x1808 (Glucose Service)");
}

void loop() {
  // Reconnection handling
  if (!deviceConnected && oldDeviceConnected) {
    delay(500);
    pServer->startAdvertising();
    Serial.println("Waiting for connection...");
    oldDeviceConnected = deviceConnected;
  }
  
  if (deviceConnected && !oldDeviceConnected) {
    oldDeviceConnected = deviceConnected;
  }
  
  if (deviceConnected) {
    // Simulate glucose reading every 5 seconds (70-120 mg/dL normal range)
    float glucose = random(70, 120) + (random(0, 10) / 10.0);
    
    // Format per Bluetooth Glucose Profile: byte 0 = flags, bytes 1-2 = value (mg/dL * 10)
    uint8_t flags = 0x01; // Blood sample
    uint16_t glucoseValue = (uint16_t)(glucose * 10);
    
    uint8_t measurement[3];
    measurement[0] = flags;
    measurement[1] = glucoseValue & 0xFF;
    measurement[2] = (glucoseValue >> 8) & 0xFF;
    
    pGlucoseMeasurement->setValue(measurement, 3);
    pGlucoseMeasurement->notify();
    
    Serial.printf("📊 Glucose: %.1f mg/dL\n", glucose);
    delay(5000);
  } else {
    delay(1000);
  }
}
