#include "config.h"
#include "mqtt_handler.h"
#include "display_handler.h"
#include "volume_controller.h"

void setup() {
  Serial.begin(115200);
  Serial.println("--- ESP32 Volume Controller starting ---");
  setupLED();  // Initialize built-in LED
  setupDisplay();  // Initialize OLED display
  connectWiFi();
  connectMQTT();
  setupControls();
  // Run the test sequence once at startup (sets volumes and mute/unmute)
  // runTestSequence();
  Serial.println("Setup complete, entering main loop");
}

void loop() {
  // Normal runtime: keep MQTT client alive and continue regular checks
  mqttLoop();
  readAndSendVolume();
  checkMuteButton();
  delay(15);
}
