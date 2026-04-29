import psycopg2
import os
import time
import pandas as pd
from sklearn.ensemble import IsolationForest
import pickle

# ---------------- DB CONFIG ----------------

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "sensors")
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "admin123")

# ---------------- CONNECT DB ----------------

def get_connection():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            print("Connected to DB")
            return conn
        except Exception as e:
            print("DB retry...", e)
            time.sleep(5)

# ---------------- LOAD DATA ----------------

def load_data():
    conn = get_connection()
    query = """
        SELECT temperature, z_score
        FROM sensor_alerts
    """
    df = pd.read_sql(query, conn)
    conn.close()

    print(f"Loaded {len(df)} rows from DB")
    return df

# ---------------- TRAIN MODEL ----------------

def train_model(df):
    if df.empty:
        raise Exception("No data available for training")

    X = df[["temperature", "z_score"]]

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    model.fit(X)

    print("Model training completed")
    return model

# ---------------- SAVE MODEL ----------------

def save_model(model):
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Model saved as model.pkl")

# ---------------- MAIN ----------------

if __name__ == "__main__":
    df = load_data()
    model = train_model(df)
    save_model(model)