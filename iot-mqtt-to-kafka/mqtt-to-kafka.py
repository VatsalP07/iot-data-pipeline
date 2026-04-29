import sys
sys.stdout.reconfigure(line_buffering=True)

import os
import json
import time
import paho.mqtt.client as mqtt
from kafka import KafkaProducer

# ---------------- CONFIG ----------------

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = 1883
MQTT_TOPIC = "sensor-data"

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = "sensor-data"

print("Starting MQTT → Kafka bridge...")

# ---------------- CONNECT KAFKA ----------------

while True:
    try:
        print("Connecting to Kafka...")
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        print("Connected to Kafka!")
        break
    except Exception as e:
        print("Kafka not ready, retrying...", e)
        time.sleep(5)

# ---------------- MQTT CALLBACKS ----------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT!")
        client.subscribe(MQTT_TOPIC)
        print("Subscribed to:", MQTT_TOPIC)
    else:
        print("MQTT connect failed:", rc)


def is_valid_data(data):
    required_fields = ["sensor_id", "temperature", "humidity", "timestamp"]

    # Check all required fields exist
    for field in required_fields:
        if field not in data:
            print(f"Invalid data: Missing field {field}")
            return False

    # Type checks
    if not isinstance(data["sensor_id"], str):
        print("Invalid data: sensor_id must be string")
        return False

    if not isinstance(data["temperature"], (int, float)):
        print("Invalid data: temperature must be number")
        return False

    if not isinstance(data["humidity"], (int, float)):
        print("Invalid data: humidity must be number")
        return False

    if not isinstance(data["timestamp"], (int, float)):
        print("Invalid data: timestamp must be number")
        return False

    return True


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        print("Received:", data)

        # Validate data
        if not is_valid_data(data):
            print("Skipping invalid data")
            return

        # Send to Kafka ONLY if valid
        producer.send(KAFKA_TOPIC, value=data)
        producer.flush()

        print("Sent to Kafka")

    except Exception as e:
        print("Processing error:", e)

# ---------------- MQTT CLIENT ----------------

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        print("Connecting to MQTT...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        break
    except Exception as e:
        print("MQTT not ready, retrying...", e)
        time.sleep(5)

client.loop_forever()