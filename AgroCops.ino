#define BLYNK_TEMPLATE_ID "TMPL3z-QAOdBI"
#define BLYNK_TEMPLATE_NAME "AgroCops"
#define BLYNK_AUTH_TOKEN "CkSDkhC2wFcIWPTNTns1fDHCuhgagx-X"
#define BLYNK_PRINT Serial

#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>
#include <DHT.h>

char ssid[] = "rithuparan";
char pass[] = "rithu@1826";

#define DHTPIN 4
#define MQ_PIN 35
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);
BlynkTimer timer;

// --- COLOR DEFINITIONS (Hex Codes) ---
#define COLOR_GREEN  "#23C48E"
#define COLOR_ORANGE "#E4B04A"
#define COLOR_RED    "#D3435C"

void sendSensorData() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int gasRaw = analogRead(MQ_PIN);

  if (isnan(h) || isnan(t)) {
    Serial.println("Error reading DHT");
    return;
  }

  // Send Data to Gauges & Chart
  Blynk.virtualWrite(V0, t);
  Blynk.virtualWrite(V1, h);
  Blynk.virtualWrite(V2, gasRaw);

  // --- SMART RISK ALGORITHM ---
  // This logic changes the Text AND Color of the widget based on severity
  
  if (gasRaw > 1000) {
    // 🔴 LEVEL 3: CRITICAL SPOILAGE
    Blynk.virtualWrite(V3, "⛔ SPOILAGE DETECTED");
    Blynk.setProperty(V3, "color", COLOR_RED);     // Change Widget to RED
    Blynk.logEvent("gas_alert", "CRITICAL: Spoilage Detected!");
    
  } else if (gasRaw > 400) {
    // 🟠 LEVEL 2: WARNING
    Blynk.virtualWrite(V3, "⚠️ Warning: VOC Rising");
    Blynk.setProperty(V3, "color", COLOR_ORANGE);  // Change Widget to ORANGE
    
  } else {
    // 🟢 LEVEL 1: SAFE
    Blynk.virtualWrite(V3, "✅ Status: FRESH");
    Blynk.setProperty(V3, "color", COLOR_GREEN);   // Change Widget to GREEN
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(MQ_PIN, INPUT);
  dht.begin();
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
  timer.setInterval(1000L, sendSensorData);
}

void loop() {
  Blynk.run();
  timer.run();
}