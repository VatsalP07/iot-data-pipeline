import os
import json
import random
import time
import signal
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sensor-data")

# 🔥 NEW: configurable anomaly probability
ANOMALY_PROBABILITY = float(os.getenv("ANOMALY_PROBABILITY", 0.0001))

client = mqtt.Client()
connected = False


def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        connected = True
        print("Connected to MQTT Broker", flush=True)
    else:
        print("Connection failed:", rc, flush=True)


client.on_connect = on_connect

print("Starting producer...", flush=True)
print(f"Anomaly probability: {ANOMALY_PROBABILITY}", flush=True)

# Retry connection
while True:
    try:
        print("Connecting to MQTT...", flush=True)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        break
    except Exception as e:
        print("MQTT not ready, retrying...", e, flush=True)
        time.sleep(3)

client.loop_start()

while not connected:
    time.sleep(1)

# ---------------- SENSOR CONFIG ----------------

SENSORS = [
    {"id": "sensor_1", "temp_range": (20, 25), "humidity_range": (30, 50)},
    {"id": "sensor_2", "temp_range": (25, 30), "humidity_range": (40, 60)},
    {"id": "sensor_3", "temp_range": (15, 22), "humidity_range": (35, 55)},
]

# ---------------- DATA GENERATION ----------------

def generate_sensor_data(sensor):
    temp = random.uniform(*sensor["temp_range"])

    # 🔥 Controlled anomaly injection
    if random.random() < ANOMALY_PROBABILITY:
        temp += random.uniform(8, 12)  # spike

    return {
        "sensor_id": sensor["id"],
        "temperature": round(temp, 2),
        "humidity": round(random.uniform(*sensor["humidity_range"]), 2),
        "timestamp": time.time()
    }

# ---------------- MAIN LOOP ----------------

def produce():
    while True:
        for sensor in SENSORS:
            data = generate_sensor_data(sensor)

            result = client.publish(MQTT_TOPIC, json.dumps(data))

            if result.rc == 0:
                print("Produced:", data, flush=True)
            else:
                print("Publish failed:", result.rc, flush=True)

        time.sleep(3)


def shutdown(sig, frame):
    print("Stopping producer...", flush=True)
    client.loop_stop()
    exit(0)


signal.signal(signal.SIGINT, shutdown)

produce()