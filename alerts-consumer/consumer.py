import json
import time
import os
from kafka import KafkaConsumer
import requests
import psycopg2
import sys
import pickle

# 🔥 FORCE LOG FLUSH
sys.stdout.reconfigure(line_buffering=True)

KAFKA_BROKER = "kafka:9092"
TOPIC = "alerts"

# 🔐 TELEGRAM ENV
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 🔐 DB ENV
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "sensors")
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "admin123")

# 🔥 THROTTLING CONFIG
COOLDOWN_SECONDS = int(os.getenv("ALERT_COOLDOWN", 60))

severity_order = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}

last_alerts = {}

# ---------------- LOAD ML MODEL ----------------

MODEL_PATH = "model.pkl"
model = None

try:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("ML model loaded in consumer")
    else:
        print("⚠️ model.pkl not found in consumer")
except Exception as e:
    print("⚠️ ML load failed:", e)

# ---------------- DB CONNECTION ----------------

def connect_db():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            print("Connected to DB", flush=True)
            return conn
        except Exception as e:
            print("DB retry...", e, flush=True)
            time.sleep(5)

conn = connect_db()
cursor = conn.cursor()

# ---------------- CREATE TABLE ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_alerts (
    id SERIAL PRIMARY KEY,
    sensor_id TEXT,
    temperature DOUBLE PRECISION,
    z_score DOUBLE PRECISION,
    severity TEXT,
    time TIMESTAMP
);
""")
conn.commit()

# ---------------- TELEGRAM ----------------

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured", flush=True)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram error:", e, flush=True)

# ---------------- ML CHECK ----------------

def is_ml_anomaly(temp, z):
    if model is None:
        return True  # fallback → don't block alerts

    prediction = model.predict([[temp, z]])[0]
    return prediction == -1

# ---------------- THROTTLING ----------------

def should_send_alert(sensor_id, severity):
    current_time = time.time()

    if sensor_id not in last_alerts:
        return True

    last = last_alerts[sensor_id]
    time_diff = current_time - last["last_time"]

    if time_diff > COOLDOWN_SECONDS:
        return True

    if severity_order[severity] > severity_order[last["last_severity"]]:
        return True

    return False


def update_alert_state(sensor_id, severity):
    last_alerts[sensor_id] = {
        "last_time": time.time(),
        "last_severity": severity
    }

# ---------------- START ----------------

print("Starting alert consumer with ML...", flush=True)

# ---------------- CONNECT TO KAFKA ----------------

while True:
    try:
        print("Connecting to Kafka...", flush=True)

        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode()),
            auto_offset_reset='latest',
            enable_auto_commit=True
        )

        print("Connected to Kafka alerts topic", flush=True)
        break

    except Exception as e:
        print("Retrying Kafka...", e, flush=True)
        time.sleep(5)

# ---------------- PROCESS STREAM ----------------

for message in consumer:
    data = message.value

    sensor_id = data["sensor_id"]
    severity = data["severity"]
    temp = data["temperature"]
    z = data["z_score"]

    # 🔥 ML FILTER
    if not is_ml_anomaly(temp, z):
        print(f"ML filtered out alert for {sensor_id}", flush=True)
        continue

    # 🔥 THROTTLING
    if not should_send_alert(sensor_id, severity):
        print(f"Throttled alert for {sensor_id} ({severity})", flush=True)
        continue

    # 🔥 STORE ALERT
    cursor.execute("""
        INSERT INTO sensor_alerts (sensor_id, temperature, z_score, severity, time)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        sensor_id,
        temp,
        z,
        severity,
        data["time"]
    ))
    conn.commit()

    # 🔥 TELEGRAM
    alert_msg = f"""
🚨 ALERT [{severity}]

Sensor: {sensor_id}
Temperature: {temp}
Z-score: {round(z, 2)}
"""

    print(alert_msg, flush=True)
    send_telegram(alert_msg)

    update_alert_state(sensor_id, severity)