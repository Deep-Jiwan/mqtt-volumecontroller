#ifndef VOLUME_CONTROLLER_H
#define VOLUME_CONTROLLER_H

#include "mqtt_handler.h"
#include "display_handler.h"

int lastVolume = -1;
bool lastMuteState = false;
int lastMuteReading = LOW; // for debounce (external pull-down => not pressed = LOW)
unsigned long lastMuteDebounceTime = 0;
const unsigned long MUTE_DEBOUNCE_MS = 50;

inline void setupControls() {
  pinMode(POT_PIN, INPUT);
  // Expect external pull-down resistor (10k) to GND and button to 3.3V
  // DO NOT drive this pin with 5V directly - it will damage the ESP32.
  pinMode(MUTE_PIN, INPUT);

  // Publish initial volume so the receiver starts in sync
  int potValue = analogRead(POT_PIN);
  int volume = map(potValue, 0, 4095, 0, 100);
  lastVolume = volume;
  Serial.print("[INIT] Initial volume read: ");
  Serial.println(volume);
  mqttPublish(MQTT_TOPIC_VOLUME, String(volume));
  // For toggle mode we don't publish a mute state from the button's static
  // reading because the button is momentary; the receiver will toggle on
  // button presses. Initialize lastMuteState as unpressed.
  lastMuteState = false;
  Serial.println("[INIT] Mute button set to TOGGLE mode (press to toggle). Ensure button uses 3.3V not 5V.");
}

inline void readAndSendVolume() {
  int potValue = analogRead(POT_PIN);
  int volume = map(potValue, 0, 4095, 0, 100);
  
  // Always update the display with current volume
  updateDisplay(volume);
  
  if (abs(volume - lastVolume) > 2) { // send only on change
    Serial.print("[VOLUME] Changed ");
    Serial.print(lastVolume);
    Serial.print(" -> ");
    Serial.println(volume);
    lastVolume = volume;
    mqttPublish(MQTT_TOPIC_VOLUME, String(volume));
  }
}

inline void checkMuteButton() {
  // Non-blocking debounce for the mute button (external pull-down, pressed = HIGH)
  int reading = digitalRead(MUTE_PIN);

  if (reading != lastMuteReading) {
    // reset the debounce timer
    lastMuteDebounceTime = millis();
  }

  if ((millis() - lastMuteDebounceTime) > MUTE_DEBOUNCE_MS) {
    // if the reading has been stable for longer than the debounce
    bool pressed = (reading == HIGH); // external pull-down: pressed == HIGH
    if (pressed != lastMuteState) {
      // Only act on the rising edge (press) to implement a toggle behaviour
      if (pressed) {
        Serial.println("[MUTE] Button pressed - publishing TOGGLE");
        mqttPublish(MQTT_TOPIC_MUTE, String("toggle"));
        // Toggle the display mute state
        setMuteState(!isMuted);
      }
      lastMuteState = pressed;
    }
  }

  lastMuteReading = reading;
}

// Helper: wait while keeping MQTT loop alive
inline void pauseWithMqtt(unsigned long ms) {
  unsigned long start = millis();
  while (millis() - start < ms) {
    mqttLoop();
    delay(10);
  }
}

// Run the requested test sequence once. This function performs the
// sequence and keeps the MQTT client alive while waiting.
inline void runTestSequence() {
  Serial.println("[TEST] Starting test sequence");

  Serial.println("[TEST] Set volume 10");
  mqttPublish(MQTT_TOPIC_VOLUME, String(10));
  pauseWithMqtt(1000);

  Serial.println("[TEST] Set volume 20");
  mqttPublish(MQTT_TOPIC_VOLUME, String(20));
  pauseWithMqtt(1000);

  Serial.println("[TEST] Set volume 30");
  mqttPublish(MQTT_TOPIC_VOLUME, String(30));
  pauseWithMqtt(1000);

  Serial.println("[TEST] Mute");
  mqttPublish(MQTT_TOPIC_MUTE, String("toggle"));
  pauseWithMqtt(1000);

  Serial.println("[TEST] Set volume 50 (while muted)");
  mqttPublish(MQTT_TOPIC_VOLUME, String(50));
  pauseWithMqtt(1000);

  Serial.println("[TEST] Unmute");
  mqttPublish(MQTT_TOPIC_MUTE, String("toggle"));
  pauseWithMqtt(1000);

  Serial.println("[TEST] Test sequence complete");
}

#endif
