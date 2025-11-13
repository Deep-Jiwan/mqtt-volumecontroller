# Windows Volume Control via MQTT

A Python application that controls Windows system volume and mute state through MQTT messages, designed for ESP32 integration.

## Overview

This project allows remote control of Windows audio output via MQTT protocol. It's designed to work with ESP32 microcontrollers but can accept commands from any MQTT client.

## Architecture

```
ESP32/MQTT Client → MQTT Broker (localhost:5020) → main.py → Windows Audio API (pycaw)
```

## Components

### `main.py` - Main MQTT Volume Controller
- **Purpose**: Subscribes to MQTT topics and controls Windows audio
- **MQTT Broker**: `localhost:5020`
- **Topics**:
  - `esp32/volume` - Volume control (accepts 0-100)
  - `esp32/mute` - Mute control (accepts "mute", "unmute", or "toggle")

### `test.py` - Volume Test Script
- **Purpose**: Sends test volume values (10, 20, 30...100) every 1 second
- **Use**: Testing volume changes and OSD display

### `mute_test.py` - Mute Test Script
- **Purpose**: Direct test of mute/unmute functionality without MQTT
- **Use**: Verifying pycaw mute operations work correctly

## How It Works

### Volume Control
1. ESP32 sends integer value `0-100` to `esp32/volume` topic
2. `main.py` receives the value and scales it linearly to `0.0-1.0` scalar
3. Uses `SetMasterVolumeLevelScalar()` to set Windows volume
4. Triggers Windows volume OSD (on-screen display) by simulating volume key presses
5. **Result**: Windows volume matches the percentage sent (50 → 50%)

### Mute Control
1. ESP32 sends `"mute"`, `"unmute"`, or `"toggle"` to `esp32/mute` topic
2. `main.py` receives the command
3. For "mute": Uses `SetMute(1)`, for "unmute": Uses `SetMute(0)`, for "toggle": Checks current state with `GetMute()` and switches it
4. **Result**: Windows audio is muted/unmuted/toggled (OSD not triggered to avoid toggle conflicts)

## Key Technical Details

### Volume Scaling
- **Input**: 0-100 (from ESP32)
- **Output**: 0.0-1.0 scalar (Windows API)
- **Method**: Linear scaling (`value / 100.0`)
- **Why Scalar**: dB scale is logarithmic and doesn't match Windows volume slider linearly

### OSD (On-Screen Display)
- **Volume Changes**: Triggers OSD by simulating `VK_VOLUME_UP`/`VK_VOLUME_DOWN` key presses that cancel each other out
- **Mute**: OSD disabled (VK_VOLUME_MUTE is a toggle and would reverse the mute state)

### Dependencies
- `paho-mqtt` - MQTT client library
- `pycaw` - Python Core Audio Windows Library
- `pywin32` - Windows API access for OSD triggers
- `comtypes` - COM interfaces for audio control

## Usage

### Start the Volume Controller
```powershell
python main.py
```

### Send Commands (from ESP32 or mosquitto_pub)
```bash
# Set volume to 75%
mosquitto_pub -h localhost -p 5020 -t esp32/volume -m "75"

# Mute audio
mosquitto_pub -h localhost -p 5020 -t esp32/mute -m "mute"

# Unmute audio
mosquitto_pub -h localhost -p 5020 -t esp32/mute -m "unmute"

# Toggle mute state
mosquitto_pub -h localhost -p 5020 -t esp32/mute -m "toggle"
```

### Run Tests
```powershell
# Test volume progression (10-100%)
python test.py

# Test mute/unmute directly
python mute_test.py
```

## Error Handling

- Invalid volume values are clamped to 0-100 range
- Invalid mute commands are rejected with error message
- MQTT connection failures are caught and reported
- Missing pywin32 gracefully degrades (no OSD, but volume still works)

## MQTT Message Format

| Topic | Valid Values | Example |
|-------|--------------|---------|
| `esp32/volume` | Integer 0-100 | `50` |
| `esp32/mute` | "mute", "unmute", or "toggle" (case-insensitive) | `toggle` |

## Console Output Example

```
Audio output: Speakers (Realtek High Definition Audio)
- Volume range: -65.25 dB - 0.0 dB
Connecting to MQTT broker at localhost:5020
✓ Connected to MQTT broker successfully
✓ Subscribed to topics: esp32/volume, esp32/mute

[VOLUME] Received: 50/100 → Set to 0.50 (50% / -32.63 dB)
[MUTE] Audio muted 🔇
[MUTE] Audio unmuted 🔊
[MUTE] Toggled: Audio muted 🔇
[VOLUME] Received: 100/100 → Set to 1.00 (100% / 0.00 dB)
```

## Notes for AI Agents

- The project uses **Windows-specific APIs** (pycaw, win32api) and won't work on Linux/Mac
- Volume scaling is **linear** (not logarithmic) to match user expectations
- OSD triggering via key simulation is a **workaround** (no direct Windows API for OSD)
- Mute key is a **toggle**, so we avoid triggering it programmatically
- The `EndpointVolume` interface provides both dB and scalar volume controls
