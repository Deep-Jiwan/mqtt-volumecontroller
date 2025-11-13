import paho.mqtt.client as mqtt
from pycaw.pycaw import AudioUtilities
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# MQTT Broker details
MQTT_BROKER = "localhost"
MQTT_PORT = 5020
MQTT_TOPIC_VOLUME = "esp32/volume"
MQTT_TOPIC_MUTE = "esp32/mute"

# Get audio device
device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume

# Get volume range (min_db, max_db, increment)
min_db, max_db, _ = volume.GetVolumeRange()

print(f"Audio output: {device.FriendlyName}")
print(f"- Volume range: {min_db} dB - {max_db} dB")
print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
print(f"Listening on topics:")
print(f"  - {MQTT_TOPIC_VOLUME} (volume: 0-100)")
print(f"  - {MQTT_TOPIC_MUTE} (mute/unmute/toggle)")
print(f"Waiting for commands...\n")


def scale_volume(value_0_100):
    """
    Scale a value from 0-100 to scalar 0.0-1.0 (matches Windows volume slider)
    
    Args:
        value_0_100: Integer value between 0 and 100
    
    Returns:
        Float value between 0.0 and 1.0
    """
    # Clamp value to 0-100 range
    value_0_100 = max(0, min(100, value_0_100))
    
    # Scale from 0-100 to 0.0-1.0
    # 0 -> 0.0 (quietest/muted)
    # 100 -> 1.0 (loudest)
    scaled_scalar = value_0_100 / 100.0
    
    return scaled_scalar


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"✓ Connected to MQTT broker successfully")
        client.subscribe(MQTT_TOPIC_VOLUME)
        client.subscribe(MQTT_TOPIC_MUTE)
        print(f"✓ Subscribed to topics: {MQTT_TOPIC_VOLUME}, {MQTT_TOPIC_MUTE}\n")
    else:
        print(f"✗ Connection failed with code {rc}")


def trigger_volume_osd():
    """Trigger the Windows volume OSD by simulating a volume key press"""
    try:
        import win32api
        import win32con
        import time
        
        # Get current volume to determine which key to press
        current_volume = volume.GetMasterVolumeLevelScalar()
        
        # Press and release the appropriate key based on current volume
        # This ensures the OSD shows without actually changing the volume
        if current_volume > 0.5:
            # If volume is high, simulate a tiny volume down then up
            win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, 0, 0)
            win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)
            win32api.keybd_event(win32con.VK_VOLUME_UP, 0, 0, 0)
            win32api.keybd_event(win32con.VK_VOLUME_UP, 0, win32con.KEYEVENTF_KEYUP, 0)
        else:
            # If volume is low, simulate a tiny volume up then down
            win32api.keybd_event(win32con.VK_VOLUME_UP, 0, 0, 0)
            win32api.keybd_event(win32con.VK_VOLUME_UP, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)
            win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, 0, 0)
            win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
    except ImportError:
        pass  # OSD won't show, but volume will still be set
    except:
        pass


def trigger_mute_osd():
    """Trigger the Windows volume OSD for mute by simulating mute key press"""
    try:
        import win32api
        import win32con
        
        # Simulate VolumeRule key press (this is the mute key)
        win32api.keybd_event(win32con.VK_VOLUME_MUTE, 0, 0, 0)
        win32api.keybd_event(win32con.VK_VOLUME_MUTE, 0, win32con.KEYEVENTF_KEYUP, 0)
    except ImportError:
        pass  # OSD won't show, but mute will still work
    except:
        pass


def on_message(client, userdata, msg):
    """Callback when a message is received"""
    try:
        topic = msg.topic
        payload = msg.payload.decode().strip().lower()
        
        if topic == MQTT_TOPIC_VOLUME:
            # Handle volume change
            value = int(payload)
            
            # Scale to 0.0-1.0 scalar range
            scalar_level = scale_volume(value)
            
            # Set the volume using scalar (matches Windows volume slider)
            volume.SetMasterVolumeLevelScalar(scalar_level, None)
            
            # Trigger Windows volume OSD
            trigger_volume_osd()
            
            # Get actual volume level after setting
            actual_scalar = volume.GetMasterVolumeLevelScalar()
            actual_db = volume.GetMasterVolumeLevel()
            
            print(f"[VOLUME] Received: {value}/100 → Set to {scalar_level:.2f} ({int(actual_scalar * 100)}% / {actual_db:.2f} dB)")
            
        elif topic == MQTT_TOPIC_MUTE:
            # Handle mute/unmute
            if payload == "mute":
                volume.SetMute(1, None)
                # Don't trigger OSD - VK_VOLUME_MUTE toggles mute state
                print(f"[MUTE] Audio muted 🔇")
            elif payload == "unmute":
                volume.SetMute(0, None)
                # Don't trigger OSD - VK_VOLUME_MUTE toggles mute state
                print(f"[MUTE] Audio unmuted 🔊")
            elif payload == "toggle":
                # Get current mute state
                current_mute = volume.GetMute()
                # Toggle: if muted (1) -> unmute (0), if unmuted (0) -> mute (1)
                new_mute = 0 if current_mute else 1
                volume.SetMute(new_mute, None)
                status = "muted 🔇" if new_mute else "unmuted 🔊"
                print(f"[MUTE] Toggled: Audio {status}")
            else:
                print(f"✗ Invalid mute command: {payload} (expected 'mute', 'unmute', or 'toggle')")
        
    except ValueError:
        print(f"✗ Invalid value received: {msg.payload.decode()} (expected integer 0-100 for volume)")
    except Exception as e:
        print(f"✗ Error: {e}")


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        print(f"✗ Unexpected disconnection from MQTT broker (code: {rc})")


# Create MQTT client
client = mqtt.Client()

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

try:
    # Connect to broker
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # Start the loop (blocking)
    client.loop_forever()
    
except KeyboardInterrupt:
    print("\n\nShutting down...")
    client.disconnect()
    print("Disconnected from MQTT broker")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"Make sure MQTT broker is running on {MQTT_BROKER}:{MQTT_PORT}")