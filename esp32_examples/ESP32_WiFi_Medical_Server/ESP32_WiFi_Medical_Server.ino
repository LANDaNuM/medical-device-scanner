/*
 * ESP32 WiFi Medical Server - Symulacja urządzenia medycznego przez WiFi
 * 
 * Ten kod tworzy serwer HTTP na ESP32, który symuluje urządzenie medyczne
 * z danymi witalnymi (puls, saturacja, temperatura)
 * 
 * Wymagania:
 * - ESP32 Board (ESP-WROOM-32)
 * - Arduino IDE z ESP32 board support
 * - WiFi network
 * 
 * Instalacja:
 * 1. Zmień SSID i hasło WiFi poniżej
 * 2. Wgraj kod na ESP32
 * 3. Sprawdź IP w Serial Monitor
 * 4. Uruchom skaner: python src/scanner.py --wifi
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// ===== KONFIGURACJA WIFI =====
const char* ssid = 5Xhb3JE8H34qb;      // Zmień na nazwę swojej sieci
const char* password = /z+]@U6Zj1+Lpd(gG[!N;       // Zmień na hasło swojej sieci
// =============================

WebServer server(80);

// Symulowane dane medyczne
struct VitalSigns {
  int heartRate;      // Puls (bpm)
  int spo2;          // Saturacja tlenu (%)
  float temperature; // Temperatura (°C)
  int bloodPressureSystolic;  // Ciśnienie skurczowe (mmHg)
  int bloodPressureDiastolic; // Ciśnienie rozkurczowe (mmHg)
};

VitalSigns currentVitals;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== ESP32 Medical Device Server ===");
  
  // Połącz z WiFi
  WiFi.begin(ssid, password);
  Serial.print("Łączenie z WiFi");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Połączono z WiFi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());
  } else {
    Serial.println("\n❌ Błąd połączenia z WiFi!");
    Serial.println("Sprawdź SSID i hasło w kodzie.");
    return;
  }
  
  // Inicjalizuj dane witalne
  updateVitals();
  
  // Endpointy API
  server.on("/", handleRoot);
  server.on("/api/vitals", handleVitals);
  server.on("/api/device/info", handleDeviceInfo);
  server.on("/api/health", handleHealth);
  
  // 404 handler
  server.onNotFound(handleNotFound);
  
  // Rozpocznij serwer
  server.begin();
  Serial.println("✅ Serwer HTTP uruchomiony!");
  Serial.println("Endpoints:");
  Serial.println("  GET /api/vitals - Dane witalne");
  Serial.println("  GET /api/device/info - Informacje o urządzeniu");
  Serial.println("  GET /api/health - Status urządzenia");
}

void loop() {
  server.handleClient();
  
  // Aktualizuj dane witalne co 2 sekundy
  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 2000) {
    updateVitals();
    lastUpdate = millis();
  }
}

void updateVitals() {
  // Symuluj realistyczne dane witalne
  currentVitals.heartRate = random(60, 100);        // 60-100 bpm (normalny zakres)
  currentVitals.spo2 = random(95, 100);            // 95-100% (normalny zakres)
  currentVitals.temperature = 36.5 + (random(0, 10) / 10.0); // 36.5-37.5°C
  currentVitals.bloodPressureSystolic = random(110, 130);    // 110-130 mmHg
  currentVitals.bloodPressureDiastolic = random(70, 85);      // 70-85 mmHg
}

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>Medical Device</title>";
  html += "<meta charset='UTF-8'>";
  html += "<style>body{font-family:Arial;margin:40px;background:#f5f5f5;}";
  html += ".card{background:white;padding:20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:20px 0;}";
  html += "h1{color:#2196F3;} .value{font-size:24px;color:#4CAF50;font-weight:bold;}</style></head><body>";
  html += "<h1>🏥 Medical Device Server</h1>";
  html += "<div class='card'><h2>Dane Witalne</h2>";
  html += "<p>Puls: <span class='value'>" + String(currentVitals.heartRate) + " bpm</span></p>";
  html += "<p>Saturacja: <span class='value'>" + String(currentVitals.spo2) + "%</span></p>";
  html += "<p>Temperatura: <span class='value'>" + String(currentVitals.temperature, 1) + "°C</span></p>";
  html += "<p>Ciśnienie: <span class='value'>" + String(currentVitals.bloodPressureSystolic) + 
          "/" + String(currentVitals.bloodPressureDiastolic) + " mmHg</span></p>";
  html += "</div>";
  html += "<div class='card'><h2>API Endpoints</h2>";
  html += "<ul><li><a href='/api/vitals'>/api/vitals</a> - JSON z danymi witalnymi</li>";
  html += "<li><a href='/api/device/info'>/api/device/info</a> - Informacje o urządzeniu</li>";
  html += "<li><a href='/api/health'>/api/health</a> - Status zdrowia</li></ul></div>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleVitals() {
  // Zwróć dane witalne jako JSON
  StaticJsonDocument<200> doc;
  doc["heart_rate"] = currentVitals.heartRate;
  doc["spo2"] = currentVitals.spo2;
  doc["temperature"] = currentVitals.temperature;
  doc["blood_pressure"] = {
    {"systolic", currentVitals.bloodPressureSystolic},
    {"diastolic", currentVitals.bloodPressureDiastolic}
  };
  doc["timestamp"] = millis();
  
  String response;
  serializeJson(doc, response);
  
  server.send(200, "application/json", response);
}

void handleDeviceInfo() {
  StaticJsonDocument<300> doc;
  doc["device_name"] = "ESP32_Medical_Device";
  doc["device_type"] = "vital_signs_monitor";
  doc["firmware_version"] = "1.0.0";
  doc["mac_address"] = WiFi.macAddress();
  doc["ip_address"] = WiFi.localIP().toString();
  doc["protocol"] = "WiFi";
  
  String response;
  serializeJson(doc, response);
  
  server.send(200, "application/json", response);
}

void handleHealth() {
  StaticJsonDocument<100> doc;
  doc["status"] = "healthy";
  doc["uptime_ms"] = millis();
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["rssi"] = WiFi.RSSI();
  
  String response;
  serializeJson(doc, response);
  
  server.send(200, "application/json", response);
}

void handleNotFound() {
  server.send(404, "text/plain", "404: Endpoint not found");
}
