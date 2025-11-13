#ifndef MQTT_HANDLER_H
#define MQTT_HANDLER_H

#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"

#define LED_PIN 2  // Built-in blue LED on most ESP32 boards

WiFiClient espClient;
PubSubClient client(espClient);

inline void setupLED() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // LED off initially
}

inline void connectWiFi() {
  Serial.print("Connecting to WiFi '");
  Serial.print(WIFI_SSID);
  Serial.println("'...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(500);
  }
  Serial.println();
  Serial.print("WiFi connected, IP: ");
  Serial.println(WiFi.localIP());
}

inline void connectMQTT() {
  client.setServer(MQTT_BROKER, MQTT_PORT);
  Serial.print("Connecting to MQTT broker ");
  Serial.print(MQTT_BROKER);
  Serial.print(":");
  Serial.print(MQTT_PORT);
  Serial.println("...");
  while (!client.connected()) {
    if (client.connect("ESP32VolumeClient")) {
      Serial.println("MQTT connected");
      digitalWrite(LED_PIN, HIGH); // Turn on blue LED when connected
    } else {
      Serial.print("MQTT connect failed, rc=");
      Serial.print(client.state());
      Serial.println(" - retrying in 1s");
      digitalWrite(LED_PIN, LOW); // Turn off LED while connecting
      delay(1000);
    }
  }
}

inline void mqttPublish(const char* topic, const String& payload) {
  Serial.print("[MQTT] Publish to '");
  Serial.print(topic);
  Serial.print("' payload: ");
  Serial.println(payload);
  if (client.connected()) {
    boolean ok = client.publish(topic, payload.c_str());
    if (!ok) {
      Serial.println("[MQTT] publish returned false");
    }
  } else {
    Serial.println("[MQTT] not connected - publish skipped");
  }
}

inline void mqttLoop() {
  // Keep connection alive and monitor status
  if (!client.connected()) {
    digitalWrite(LED_PIN, LOW); // Turn off LED if disconnected
    // Attempt to reconnect
    connectMQTT();
  }
  client.loop();
}

#endif
