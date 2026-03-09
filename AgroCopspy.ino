#define BLYNK_TEMPLATE_ID "TMPL3z-QAOdBI"
#define BLYNK_TEMPLATE_NAME "AgroCops"
#define BLYNK_AUTH_TOKEN "CkSDkhC2wFcIWPTNTns1fDHCuhgagx-X"
#define BLYNK_PRINT Serial

#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>
#include <DHT.h>

char ssid[] = "harsha";
char pass[] = "harsha@0984";

#define DHTPIN 4
#define MQ_PIN 35
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);
BlynkTimer timer;

void sendSensorData() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int gasRaw = analogRead(MQ_PIN);

  if (isnan(h) || isnan(t)) {
    return;
  }

  // --- CRITICAL FOR PYTHON DASHBOARD ---
  // The Python script looks for "Gas Level: <number>"
  Serial.print("Temp: ");
  Serial.print(t);
  Serial.print(" | Gas Level: "); 
  Serial.println(gasRaw);         
  // -------------------------------------

  // Send to Blynk App
  Blynk.virtualWrite(V0, t);
  Blynk.virtualWrite(V1, h);
  Blynk.virtualWrite(V2, gasRaw);

  // Send Status Text
  if (gasRaw > 1000) {
    Blynk.virtualWrite(V3, "⛔ SPOILAGE DETECTED");
  } else if (gasRaw > 400) {
    Blynk.virtualWrite(V3, "⚠️ Warning: VOC Rising");
  } else {
    Blynk.virtualWrite(V3, "✅ Status: FRESH");
  }
}

void setup() {
  Serial.begin(115200);  // Must match Python BAUD_RATE
  pinMode(MQ_PIN, INPUT);
  dht.begin();
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
  timer.setInterval(1000L, sendSensorData);
}

void loop() {
  Blynk.run();
  timer.run();
}
