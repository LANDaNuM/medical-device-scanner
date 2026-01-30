/*
 * ESP32 Glukometr BLE - Symulacja urządzenia medycznego
 * 
 * Ten kod symuluje glukometr Bluetooth Low Energy (BLE)
 * używając standardowego UUID dla Glucose Service (0x1808)
 * 
 * Wymagania:
 * - ESP32 Board (ESP-WROOM-32)
 * - Arduino IDE z ESP32 board support
 * - Biblioteka: ESP32 BLE Arduino (wbudowana)
 * 
 * Instalacja:
 * 1. Zainstaluj ESP32 board support w Arduino IDE
 * 2. Wgraj ten kod na ESP32
 * 3. Uruchom skaner na Raspberry Pi: python src/scanner.py --ble
 */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// UUID dla Glucose Service (standard medyczny Bluetooth)
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

// Callback dla połączenia/disconnection
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
  Serial.println("\n=== ESP32 Glukometr BLE ===");
  
  // Inicjalizuj BLE
  BLEDevice::init("GlucoSmart_Pro");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  // Utwórz Glucose Service
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
  
  // Dodaj descriptor dla notifications
  pGlucoseMeasurement->addDescriptor(new BLE2902());
  
  // Ustaw wartości początkowe
  uint8_t featureValue[2] = {0x01, 0x00}; // Basic features
  pGlucoseFeature->setValue(featureValue, 2);
  
  // Rozpocznij service
  pService->start();
  
  // Rozpocznij advertising
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(GLUCOSE_SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // Pomaga z iPhone connection issue
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  
  Serial.println("Glukometr BLE uruchomiony i reklamowany!");
  Serial.println("Nazwa: GlucoSmart_Pro");
  Serial.println("Service UUID: 0x1808 (Glucose Service)");
}

void loop() {
  // Obsługa reconnection
  if (!deviceConnected && oldDeviceConnected) {
    delay(500);
    pServer->startAdvertising();
    Serial.println("Czekam na połączenie...");
    oldDeviceConnected = deviceConnected;
  }
  
  if (deviceConnected && !oldDeviceConnected) {
    oldDeviceConnected = deviceConnected;
  }
  
  // Symuluj pomiar glukozy co 5 sekund
  if (deviceConnected) {
    // Generuj losowy pomiar glukozy (70-120 mg/dL - normalny zakres)
    float glucose = random(70, 120) + (random(0, 10) / 10.0);
    
    // Format danych zgodny z Bluetooth Glucose Profile
    // Byte 0: Flags (0x01 = cukier we krwi, 0x02 = kontekst, etc.)
    // Byte 1-2: Glucose value (16-bit, jednostka: mg/dL)
    uint8_t flags = 0x01; // Blood sample
    uint16_t glucoseValue = (uint16_t)(glucose * 10); // W mg/dL * 10
    
    uint8_t measurement[3];
    measurement[0] = flags;
    measurement[1] = glucoseValue & 0xFF;
    measurement[2] = (glucoseValue >> 8) & 0xFF;
    
    // Wyślij przez BLE
    pGlucoseMeasurement->setValue(measurement, 3);
    pGlucoseMeasurement->notify();
    
    Serial.printf("📊 Pomiar glukozy: %.1f mg/dL\n", glucose);
    delay(5000);
  } else {
    delay(1000);
  }
}
