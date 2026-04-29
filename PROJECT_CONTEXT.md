# IoT Real-Time Data Pipeline

## Project Goal
Build a real-time pipeline:
MQTT → Kafka → Spark → TimescaleDB → Grafana

---

## Current Status (Day 1)
- MQTT → Kafka pipeline working
- Removed database writes from MQTT service
- Kafka verified using Kafdrop
- GitHub repository initialized

### Day 2
- Added multi-sensor simulation
- Each sensor has unique temperature and humidity ranges
- Improved realism of IoT data generationz

### Day 3
- Added data validation layer in MQTT → Kafka service
- Enforced schema (sensor_id, temperature, humidity, timestamp)
- Invalid data is now filtered before reaching Kafka

### Day 4
- Integrated Spark Structured Streaming
- Spark consumes real-time data from Kafka topic `sensor-data`
- Implemented schema-based JSON parsing
- Data is processed in micro-batches and printed to console
- Added Kafka connector package to Spark

### Day 5
- Integrated TimescaleDB for persistent storage
- Spark writes streaming data using foreachBatch
- Converted epoch timestamps to readable format
- Used JDBC for database integration

### Day 6
- Implemented window-based aggregation in Spark
- Computed average temperature per sensor
- Introduced watermarking for handling late data
- Created new table `sensor_aggregates`
- Spark now writes both raw and aggregated data streams

### Day 7
- Connected Grafana to TimescaleDB
- Created real-time dashboards
- Visualized aggregated sensor data
- Built time-series graphs per sensor
- Enabled live auto-refresh for streaming data


### Day 8
- Implemented real-time anomaly detection using Z-score method
- Computed rolling mean and standard deviation per sensor
- Joined raw stream with windowed statistics using time-based join
- Calculated Z-score for each incoming data point
- Detected anomalies using |z_score| > 2 rule
- Added anomaly injection in producer for testing
- Created new table `sensor_anomalies` with detailed metrics
- Successfully detected real-time temperature spikes


### Day 9
- Implemented Kafka-based alerts system
- Spark streams anomalies to `alerts` topic
- Built alerts-consumer microservice
- Integrated Telegram notifications
- Used environment variables for secure credentials

### Day 10 (Final Stabilization)
- Removed debug console stream from Spark
- Tuned Z-score thresholds for realistic anomaly detection
- Finalized production-ready streaming pipeline

### Day 11 (FINAL ML IMPLEMENTATION)

ML Model Training
- Implemented Isolation Forest using scikit-learn
- Trained on `sensor_alerts` table
- Features used:
  - temperature
  - z_score
- Model trained inside Docker container to avoid version mismatch
- Model saved as `model.pkl`


ML Inference API
- Added `/predict` endpoint in FastAPI
- Input:
  - temperature
  - z_score
- Output:
  - anomaly: true/false
- Model loaded safely with exception handling



Critical Fixes
- Fixed pickle compatibility issue (local vs Docker mismatch)
- Ensured model training inside container
- Prevented API crash on model load failure
- Understood Docker file isolation



✅ ML + Alerts Integration (MAJOR UPGRADE)
- Integrated ML into `alerts-consumer`
- Alerts now pass through:

  Z-score → ML validation → Alert

- Implemented fallback if model not available
- Reduced false positives significantly
---

## Tech Stack
- MQTT (Mosquitto)
- Kafka
- Spark (coming next)
- TimescaleDB
- Grafana
- Python
- Docker

---

## Data Format
{
  "sensor_id": "sensor_1",
  "temperature": float,
  "humidity": float,
  "timestamp": float
}

---

## Project Structure

seabeacon/
│── docker-compose.yml
│── PROJECT_CONTEXT.md
│── iot-mqtt-to-kafka/
│── iot-sensor-messages-producer/
│── mosquitto/

---

## How to Run

docker-compose up --build

---

## Next Step
Add multi-sensor support

## 🔌 Future Enhancements

- Integration with external APIs (e.g., weather data)
- Support for hybrid data ingestion (simulated + real-world data)
- Extendable producer architecture for multiple data sources