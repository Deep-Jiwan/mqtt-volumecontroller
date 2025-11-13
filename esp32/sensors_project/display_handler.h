#ifndef DISPLAY_HANDLER_H
#define DISPLAY_HANDLER_H

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Sound icon (16x16)
#define SOUND_WIDTH 16
#define SOUND_HEIGHT 16
// 'speaker', 16x16px
static const unsigned char PROGMEM sound_icon[] = {
  0x00, 0x00, 0x00, 0x70, 0x00, 0xf0, 0x01, 0xf0, 0x03, 0xf0, 0x07, 0xf0, 0x3f, 0xf0, 0x3f, 0xf0, 
  0x3f, 0xf0, 0x3f, 0xf0, 0x07, 0xf0, 0x03, 0xf0, 0x01, 0xf0, 0x00, 0xf0, 0x00, 0x70, 0x00, 0x00
};

// 'mute speaker', 16x16px
static const unsigned char PROGMEM mute_icon[] = {
  0xc0, 0x00, 0xe0, 0x70, 0x70, 0xf0, 0x39, 0xf0, 0x1f, 0xf0, 0x0f, 0xf0, 0x3f, 0xf0, 0x3f, 0xf0, 
  0x3f, 0xf0, 0x3f, 0xf0, 0x07, 0xf0, 0x03, 0xf8, 0x01, 0xfc, 0x00, 0xfe, 0x00, 0x77, 0x00, 0x03
};

int currentVolume = 0;
bool isMuted = false;

inline void setupDisplay() {
  Wire.begin(21, 22);
  
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("[DISPLAY] SSD1306 allocation failed"));
    for (;;);
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Initializing...");
  display.display();
  
  Serial.println("[DISPLAY] OLED initialized");
}

inline void updateDisplay(int volumeLevel) {
  currentVolume = volumeLevel;
  
  // Determine if we should show mute icon (when volume is 0 or explicitly muted)
  bool showMuteIcon = (volumeLevel == 0) || isMuted;
  
  display.clearDisplay();
  String title = "Volume:";
  int16_t x1, y1;
  uint16_t w, h;
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.getTextBounds(title, 0, 0, &x1, &y1, &w, &h);
  display.setCursor((SCREEN_WIDTH - w) / 2, 0);
  display.println(title);

  // ---- Line 2: Icon + Progress Bar + Value ----
  int barWidth = 80;
  int barHeight = 10;
  int barX = 24; // centered considering 128 width
  int barY = 20;
  int filled = map(volumeLevel, 0, 100, 0, barWidth);

  // Show appropriate icon (mute or sound)
  if (showMuteIcon) {
    display.drawBitmap(barX - 20, barY - 3, mute_icon, SOUND_WIDTH, SOUND_HEIGHT, SSD1306_WHITE);
  } else {
    display.drawBitmap(barX - 20, barY - 3, sound_icon, SOUND_WIDTH, SOUND_HEIGHT, SSD1306_WHITE);
  }
  
  display.drawRect(barX, barY, barWidth, barHeight, SSD1306_WHITE);
  display.fillRect(barX, barY, filled, barHeight, SSD1306_WHITE);

  // Numeric value (right aligned with bar)
  String value = String(volumeLevel);
  display.getTextBounds(value, 0, 0, &x1, &y1, &w, &h);
  display.setCursor(barX + barWidth + ((SCREEN_WIDTH - (barX + barWidth)) - w) / 2, barY);
  display.println(value);

  // ---- Line 4: IP address ----
  String ip = WiFi.localIP().toString();
  display.getTextBounds(ip, 0, 0, &x1, &y1, &w, &h);
  display.setCursor((SCREEN_WIDTH - w) / 2, 50);
  display.println(ip);

  display.display();
}

inline void setMuteState(bool muted) {
  isMuted = muted;
  // Immediately update display to reflect mute state
  updateDisplay(currentVolume);
}

#endif
