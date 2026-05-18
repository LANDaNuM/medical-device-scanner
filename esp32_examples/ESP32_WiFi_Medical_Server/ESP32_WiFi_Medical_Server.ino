/*
 * ESP32 WiFi Medical Server - Medical device simulation over WiFi
 *
 * This code runs an HTTP server on ESP32 that simulates a medical device
 * with vital signs (heart rate, SpO2, temperature).
 *
 * Requirements:
 * - ESP32 Board (ESP-WROOM-32)
 * - Arduino IDE with ESP32 board support
 * - WiFi network
 *
 * Setup:
 * 1. Set SSID and password below
 * 2. Upload to ESP32
 * 3. Check IP in Serial Monitor
 * 4. Run scanner: python src/scanner.py --wifi
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// ===== WIFI CONFIG =====
const char* ssid = "YOUR_SSID";        // Set your network name
const char* password = "YOUR_PASSWORD"; // Set your network password
// =======================

WebServer server(80);

// Simulated medical data
struct VitalSigns {
  int heartRate;      // Heart rate (bpm)
  int spo2;           // SpO2 (%)
  float temperature;  // Temperature (°C)
  int bloodPressureSystolic;   // Systolic (mmHg)
  int bloodPressureDiastolic;  // Diastolic (mmHg)
};

VitalSigns currentVitals;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== ESP32 Medical Device Server ===");
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Connected to WiFi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    Serial.println("Check SSID and password in code.");
    return;
  }
  
  // Init vitals
  updateVitals();
  
  // API endpoints
  server.on("/", handleRoot);
  server.on("/api/vitals", handleVitals);
  server.on("/api/device/info", handleDeviceInfo);
  server.on("/api/health", handleHealth);
  
  server.onNotFound(handleNotFound);
  
  server.begin();
  Serial.println("✅ HTTP server started!");
  Serial.println("Endpoints:");
  Serial.println("  GET /api/vitals - Vital signs");
  Serial.println("  GET /api/device/info - Device info");
  Serial.println("  GET /api/health - Device status");
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
  // Simulate realistic vital signs
  currentVitals.heartRate = random(60, 100);        // 60-100 bpm
  currentVitals.spo2 = random(95, 100);            // 95-100%
  currentVitals.temperature = 36.5 + (random(0, 10) / 10.0); // 36.5-37.5°C
  currentVitals.bloodPressureSystolic = random(110, 130);    // 110-130 mmHg
  currentVitals.bloodPressureDiastolic = random(70, 85);     // 70-85 mmHg
}

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>Medical Device</title>";
  html += "<meta charset='UTF-8'>";
  html += "<style>body{font-family:Arial;margin:40px;background:#f5f5f5;}";
  html += ".card{background:white;padding:20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:20px 0;}";
  html += "h1{color:#2196F3;} .value{font-size:24px;color:#4CAF50;font-weight:bold;}</style></head><body>";
  html += "<h1>🏥 Medical Device Server</h1>";
  html += "<div class='card'><h2>Vital Signs</h2>";
  html += "<p>Heart rate: <span class='value'>" + String(currentVitals.heartRate) + " bpm</span></p>";
  html += "<p>SpO2: <span class='value'>" + String(currentVitals.spo2) + "%</span></p>";
  html += "<p>Temperature: <span class='value'>" + String(currentVitals.temperature, 1) + "°C</span></p>";
  html += "<p>Blood pressure: <span class='value'>" + String(currentVitals.bloodPressureSystolic) + 
          "/" + String(currentVitals.bloodPressureDiastolic) + " mmHg</span></p>";
  html += "</div>";
  html += "<div class='card'><h2>API Endpoints</h2>";
  html += "<ul><li><a href='/api/vitals'>/api/vitals</a> - Vital signs JSON</li>";
  html += "<li><a href='/api/device/info'>/api/device/info</a> - Device info</li>";
  html += "<li><a href='/api/health'>/api/health</a> - Health status</li></ul></div>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleVitals() {
  // Return vitals as JSON
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
