from fastapi import FastAPI, Query
from db import get_connection
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pickle
import os

# 🔥 APP INIT
app = FastAPI(title="IoT Alerts API")

# 🔥 CORS FIX (IMPORTANT)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (safe for demo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DB CONNECTION ----------------

conn = get_connection()
cursor = conn.cursor()

# ---------------- LOAD MODEL ----------------

MODEL_PATH = "model.pkl"
model = None

try:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("ML model loaded")
    else:
        print("⚠️ model.pkl not found")
except Exception as e:
    print("⚠️ Failed to load model:", e)
    model = None

# ---------------- REQUEST SCHEMA ----------------

class PredictRequest(BaseModel):
    temperature: float
    z_score: float

# =====================================================
# 🔥 1. GET ALERTS (WITH FILTERS)
# =====================================================

@app.get("/alerts")
def get_alerts(
    severity: str = Query(None),
    sensor_id: str = Query(None),
    limit: int = Query(50)
):
    try:
        query = """
            SELECT sensor_id, temperature, z_score, severity, time
            FROM sensor_alerts
        """

        conditions = []
        params = []

        if severity:
            conditions.append("severity = %s")
            params.append(severity)

        if sensor_id:
            conditions.append("sensor_id = %s")
            params.append(sensor_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY time DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        result = []
        for r in rows:
            result.append({
                "sensor_id": r[0],
                "temperature": r[1],
                "z_score": r[2],
                "severity": r[3],
                "time": str(r[4])
            })

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# =====================================================
# ✅ 2. GET ALERTS BY SENSOR
# =====================================================

@app.get("/alerts/{sensor_id}")
def get_alerts_by_sensor(sensor_id: str, limit: int = 50):
    try:
        cursor.execute("""
            SELECT sensor_id, temperature, z_score, severity, time
            FROM sensor_alerts
            WHERE sensor_id = %s
            ORDER BY time DESC
            LIMIT %s
        """, (sensor_id, limit))

        rows = cursor.fetchall()

        result = []
        for r in rows:
            result.append({
                "sensor_id": r[0],
                "temperature": r[1],
                "z_score": r[2],
                "severity": r[3],
                "time": str(r[4])
            })

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# =====================================================
# ✅ 3. GET STATS
# =====================================================

@app.get("/stats")
def get_stats():
    try:
        cursor.execute("""
            SELECT severity, COUNT(*)
            FROM sensor_alerts
            GROUP BY severity
        """)

        rows = cursor.fetchall()

        result = {}
        for r in rows:
            result[r[0]] = r[1]

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# =====================================================
# 🔥 4. ML PREDICTION
# =====================================================

@app.post("/predict")
def predict(data: PredictRequest):
    try:
        if model is None:
            return JSONResponse(status_code=500, content={"error": "Model not loaded"})

        X = [[data.temperature, data.z_score]]

        prediction = model.predict(X)[0]

        is_anomaly = True if prediction == -1 else False

        return {
            "anomaly": is_anomaly
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})