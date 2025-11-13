#ifndef CONFIG_H
#define CONFIG_H

#define WIFI_SSID "ap"
#define WIFI_PASSWORD "pass"

#define MQTT_BROKER "192.168.193.30"   // IP of your laptop or MQTT broker
#define MQTT_PORT 5020
#define MQTT_TOPIC_VOLUME "esp32/volume"
#define MQTT_TOPIC_MUTE "esp32/mute"
#define MQTT_TOPIC_PC_SOUND "pc/sound"  // Subscribe to PC volume updates

#define POT_PIN 34
#define MUTE_PIN 25

#endif
