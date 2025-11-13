import paho.mqtt.client as mqtt
import time

# MQTT Broker details
MQTT_BROKER = "localhost"
MQTT_PORT = 5020
MQTT_TOPIC = "esp32/volume"

# Create MQTT client
client = mqtt.Client()

print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")

try:
    # Connect to broker
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print(f"✓ Connected successfully")
    print(f"Publishing to topic: {MQTT_TOPIC}")
    print("Starting volume test sequence (10-100 in steps of 10)...\n")
    
    # Send volume values from 10 to 100, incrementing by 10
    for volume in range(10, 101, 10):
        print(f"Publishing: {volume}")
        client.publish(MQTT_TOPIC, str(volume))
        time.sleep(1)
    
    print("\n✓ Test sequence completed!")
    
except KeyboardInterrupt:
    print("\n\nTest interrupted by user")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"Make sure MQTT broker is running on {MQTT_BROKER}:{MQTT_PORT}")
    
finally:
    client.disconnect()
    print("Disconnected from MQTT broker")
