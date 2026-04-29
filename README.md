# 📡 Real-Time IoT Monitoring System

## 🚀 Overview
This project implements a real-time IoT data monitoring pipeline that ingests sensor data, processes it using streaming analytics, detects anomalies using statistical and machine learning techniques, and generates alerts with live visualization.

The system is built using a modern data engineering stack including Kafka, Spark Streaming, TimescaleDB, and FastAPI.

---

## 🧠 Key Features

- Real-time data ingestion using MQTT and Kafka  
- Stream processing using Apache Spark  
- Z-score based anomaly detection  
- Machine Learning validation using Isolation Forest  
- Intelligent alert system with severity levels  
- Telegram alert notifications  
- FastAPI backend for APIs  
- Interactive frontend dashboard  
- Grafana integration for visualization  
- Fully containerized using Docker  

---

## 🏗️ System Architecture

IoT Sensors → MQTT → Kafka → Spark Streaming → TimescaleDB → FastAPI → Dashboard  
                                                     ↓  
                                                 Alerts → Kafka → Consumer → Telegram  

---

## 🧪 Anomaly Detection Logic

- Z-score is calculated using rolling window statistics (mean and standard deviation)
- Severity levels:
  - LOW
  - MEDIUM
  - HIGH
  - CRITICAL
- Alerts are further validated using an Isolation Forest ML model

---

## 🛠️ Tech Stack

- Data Ingestion: MQTT (Mosquitto)  
- Streaming: Apache Kafka  
- Processing: Apache Spark Structured Streaming  
- Database: TimescaleDB (PostgreSQL)  
- Backend: FastAPI  
- Frontend: HTML, CSS, JavaScript  
- Visualization: Grafana  
- Machine Learning: Scikit-learn (Isolation Forest)  
- Containerization: Docker & Docker Compose  

---

## ⚙️ How to Run

### 1. Clone the repository
git clone https://github.com/VatsalP07/iot-data-pipeline.git  
cd iot-data-pipeline  

### 2. Start the system
docker-compose up --build  

---

## 🌐 Access Points

- Grafana Dashboard → http://localhost:3000  
- FastAPI Backend → http://localhost:8000  
- Kafka UI (Kafdrop) → http://localhost:9001  

---

## 🔮 ML Integration

- Model: Isolation Forest  
- Features used:
  - Temperature  
  - Z-score  
- Helps reduce false positives in anomaly detection  

---

## 📦 Project Structure

seabeacon/  
│── docker-compose.yml  
│── api-service/  
│── spark-streaming/  
│── alerts-consumer/  
│── iot-mqtt-to-kafka/  
│── iot-sensor-messages-producer/  
│── frontend/  

---

## 📈 Future Enhancements

- Integration with real IoT devices  
- Advanced ML models (LSTM, Autoencoders)  
- Cloud deployment (AWS/GCP)  
- Mobile app for alerts  

---

## 👨‍💻 Author

Vatsal Pal  
B.Tech CSE  

---

## 📌 Conclusion

This project demonstrates a scalable real-time IoT pipeline capable of processing streaming data, detecting anomalies intelligently, and generating actionable alerts with visualization.
