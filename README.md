# MQTT Volume Controller

Lightweight project that uses an ESP32 hardware controller (potentiometer + mute button) to publish volume and mute commands over MQTT to a Windows client that applies the changes to the system audio (via pycaw).

## Repository layout

- `esp32/sensors_project/` — ESP32 Arduino sketch and headers (potentiometer, mute button, MQTT client).
- `clientside/` — Windows Python client using pycaw to adjust system volume and respond to MQTT messages. Contains a vendored `pycaw` implementation used by `main.py`.
- `tests/` — integration tests.

## High level architecture

Mermaid diagram (rendered on platforms that support Mermaid):

```mermaid
graph LR
  ESP32[ESP32 Sensor Board]\n  Broker[MQTT Broker (e.g. Mosquitto)]\n  Client[Windows Client (pycaw)]
  ESP32 -->|publish\nesp32/volume, esp32/mute| Broker
  Client -->|subscribe\nesp32/volume, esp32/mute| Broker
```

ASCII alternative:

ESP32 (pot + button)  --> MQTT Broker (Mosquitto) <-- Windows Client (pycaw)
       publishes: esp32/volume (0-100)
                 esp32/mute (toggle/mute/unmute)

Flow:
- User turns potentiometer or presses mute on the ESP32
- ESP32 publishes to MQTT topics `esp32/volume` and `esp32/mute`
- Windows client subscribes and applies volume/mute using Windows audio APIs

## Topics and default configuration

ESP32 default configuration (`esp32/sensors_project/config.h`):

- WIFI_SSID: `ap`
- WIFI_PASSWORD: `pass`
- MQTT_BROKER: `192.168.193.30` (change this to your broker IP)
- MQTT_PORT: `5020`
- MQTT_TOPIC_VOLUME: `esp32/volume`
- MQTT_TOPIC_MUTE: `esp32/mute`

Client defaults (`clientside/main.py`):

- MQTT_BROKER: `localhost` (edit to point to your broker IP)
- MQTT_PORT: `5020`
- MQTT_TOPIC_VOLUME: `esp32/volume`
- MQTT_TOPIC_MUTE: `esp32/mute`

Note: both sides must agree on the broker address/port and topic names.

## Hardware wiring notes

- POT_PIN: `34` — connect a 3.3V-tolerant potentiometer to ADC pin 34 (wiper to 34, ends to 3.3V and GND).
- MUTE_PIN: `25` — momentary button with external pull-down to GND and button to 3.3V. The code expects a pull-down; pressing the button reads HIGH.
- DO NOT drive inputs with 5V. ESP32 is 3.3V logic.

## ESP32: build & flash (recommended: Arduino IDE or Arduino CLI)

1. Open `esp32/sensors_project/sensors_project.ino` in the Arduino IDE.
2. Edit `esp32/sensors_project/config.h` to set `WIFI_SSID`, `WIFI_PASSWORD` and `MQTT_BROKER`/`MQTT_PORT` to match your network and broker.
3. Select your ESP32 board in Tools → Board and the correct COM/serial port.
4. Upload.

Using Arduino CLI (example, replace with your board FQBN and port):

PowerShell example (replace placeholders):

```powershell
# install or configure Arduino CLI first: https://arduino.github.io/arduino-cli/latest/installation/
arduino-cli core update-index
arduino-cli core install esp32:esp32

# compile
arduino-cli compile --fqbn esp32:esp32:esp32 f:\Projects\mqttvolume\mqtt-volumecontroller\esp32\sensors_project

# upload (set port and fqbn)
arduino-cli upload -p COM3 --fqbn esp32:esp32:esp32 f:\Projects\mqttvolume\mqtt-volumecontroller\esp32\sensors_project
```

If using PlatformIO, create a `platformio.ini` and use `pio run -t upload`.

## MQTT Broker

This project is broker-agnostic. For local testing, Mosquitto is recommended.

Install Mosquitto on Windows (choco) or on Linux:

Windows (PowerShell with Chocolatey):

```powershell
choco install mosquitto
```

Linux (Debian/Ubuntu):

```bash
sudo apt update; sudo apt install -y mosquitto mosquitto-clients
```

Start mosquitto (or use system service). By default it listens on port 1883; this project uses 5020 in examples — either configure the broker or edit the port values in `config.h` and `main.py`.

## Windows client: setup and run

The Windows client is in `clientside/` and uses the vendored `pycaw` module present in that folder.

Prerequisites:

- Python 3.8+ on Windows (PowerShell examples assume `python` is available)
- Windows-only dependencies: `pywin32`, `comtypes`
- MQTT client: `paho-mqtt`

Quick start (PowerShell):

```powershell
cd f:\Projects\mqttvolume\mqtt-volumecontroller\clientside
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install paho-mqtt pywin32 comtypes

# Edit main.py and set MQTT_BROKER to your broker IP (or use localhost if running on same machine)
python main.py
```

Notes:
- `main.py` uses the vendored `pycaw` package contained in `clientside/pycaw/`. Running from the `clientside` directory ensures Python will import it.
- If you prefer, you can `pip install pycaw` globally instead of using the vendored copy.

## Manual MQTT testing

Use `mosquitto_pub` to send commands:

```powershell
# Set volume to 42
mosquitto_pub -h <broker-ip> -p 5020 -t esp32/volume -m 42

# Toggle mute
mosquitto_pub -h <broker-ip> -p 5020 -t esp32/mute -m toggle

# Mute explicitly
mosquitto_pub -h <broker-ip> -p 5020 -t esp32/mute -m mute

# Unmute
mosquitto_pub -h <broker-ip> -p 5020 -t esp32/mute -m unmute
```

## Tests

- There are tests under `clientside/` and top-level `tests/`. They are lightweight integration checks and examples. See `clientside/test_mqtt_integration.py` for an MQTT-only test.

## Troubleshooting

- If the Windows client cannot connect: ensure broker IP/port is correct and no firewall is blocking the port.
- If the ESP32 cannot connect to WiFi: confirm SSID/password in `config.h` and verify WiFi signal.
- If audio changes do not apply: ensure `main.py` is running with Administrator privileges if needed and that `pycaw` dependencies (`pywin32`, `comtypes`) are installed.

## Next steps / improvements

- Add environment-based configuration for the Python client (read broker from env vars or a config file instead of editing `main.py`).
- Add a `platformio.ini` for reproducible ESP32 builds and CI.
- Add unit tests and CI for the Python client.

