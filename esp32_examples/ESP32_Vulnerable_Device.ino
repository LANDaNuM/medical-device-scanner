/*
 * ESP32 Vulnerable Device - Symulacja urządzenia z podatnościami bezpieczeństwa
 * 
 * TEN KOD CELOWO TWORZY PODATNOŚCI BEZPIECZEŃSTWA!
 * Używaj TYLKO do testowania skanera bezpieczeństwa.
 * 
 * Podatności:
 * - Brak szyfrowania BLE
 * - Brak autoryzacji (każdy może się połączyć)
 * - Otwarte dane medyczne
 * - Brak wymagania parowania
 * 
 * Wymagania:
 * - ESP32 Board (ESP-WROOM-32)
 * - Arduino IDE z ESP32 board support
 * 
 * Instalacja:
 * 1. Wgraj kod na ESP32
 * 2. Uruchom skaner: python src/scanner.py --ble
 * 3. Skaner powinien wykryć podatności!
 */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;

// UUID dla testowego urządzenia (NIE standardowe UUID medyczne)
#define SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID  "87654321-4321-4321-4321-cba987654321"

// Callback dla połączenia (bez autoryzacji!)
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      Serial.println("⚠️ POŁĄCZENIE BEZ AUTORYZACJI!");
      Serial.println("   Każdy może się połączyć - TO JEST PODATNOŚĆ!");
    }

    void onDisconnect(BLEServer* pServer) {
      Serial.println("Rozłączono");
    }
};

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== ⚠️ PODATNE URZĄDZENIE BLE ===");
  Serial.println("CELOWO TWORZY PODATNOŚCI BEZPIECZEŃSTWA!");
  Serial.println("Używaj TYLKO do testowania skanera.\n");
  
  // Inicjalizuj BLE BEZ szyfrowania
  BLEDevice::init("Vulnerable_Medical_Device");
  pServer = BLEDevice::createServer();
  
  // Ustaw callback (ale nie wymaga autoryzacji)
  pServer->setCallbacks(new MyServerCallbacks());
  
  // Utwórz service
  BLEService* pService = pServer->createService(SERVICE_UUID);
  
  // Characteristic BEZ autoryzacji i BEZ szyfrowania
  // PROPERTY_READ | PROPERTY_WRITE - każdy może odczytać/zapisać
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ |
    BLECharacteristic::PROPERTY_WRITE |
    BLECharacteristic::PROPERTY_NOTIFY
  );
  
  // Ustaw wrażliwe dane medyczne BEZ szyfrowania
  String sensitiveData = "Patient_ID:12345,Glucose:95,HeartRate:72";
  pCharacteristic->setValue(sensitiveData.c_str());
  
  // Rozpocznij service
  pService->start();
  
  // Rozpocznij advertising (bez wymagania parowania)
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  BLEDevice::startAdvertising();
  
  Serial.println("❌ PODATNOŚCI:");
  Serial.println("   1. Brak szyfrowania BLE");
  Serial.println("   2. Brak autoryzacji (każdy może się połączyć)");
  Serial.println("   3. Dane medyczne dostępne bez hasła");
  Serial.println("   4. Brak wymagania parowania");
  Serial.println("\n✅ Urządzenie reklamowane i gotowe do skanowania!");
  Serial.println("   Uruchom skaner: python src/scanner.py --ble");
}

void loop() {
  // Symuluj wysyłanie danych co 3 sekundy (bez szyfrowania!)
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 3000) {
    // Generuj losowe dane medyczne
    int glucose = random(70, 120);
    int heartRate = random(60, 100);
    
    String data = "Glucose:" + String(glucose) + ",HR:" + String(heartRate);
    
    // Wyślij BEZ szyfrowania
    pCharacteristic->setValue(data.c_str());
    pCharacteristic->notify();
    
    Serial.printf("📤 Wysłano dane (BEZ szyfrowania): %s\n", data.c_str());
    lastSend = millis();
  }
  
  delay(100);
}
