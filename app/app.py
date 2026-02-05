from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import os

# -------------------------------
# Path handling (VERY IMPORTANT)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "xgb_solar_model.pkl")
FEATURE_PATH = os.path.join(BASE_DIR, "models", "xgb_features.pkl")

# -------------------------------
# Load model & features
# -------------------------------
model = joblib.load(MODEL_PATH)
FEATURES = joblib.load(FEATURE_PATH)

# -------------------------------
# FastAPI app
# -------------------------------
app = FastAPI(title="Solar Power Prediction API")

# -------------------------------
# Input schema
# (you can extend this later)
# -------------------------------
class SolarInput(BaseModel):
    DC_POWER: float
    hour: int
    day: int
    month: int

# -------------------------------
# Health check
# -------------------------------
@app.get("/")
def home():
    return {
        "status": "API is running",
        "model_loaded": True
    }

# -------------------------------
# Prediction endpoint
# -------------------------------
@app.post("/predict")
def predict(data: SolarInput):

    # Convert input to DataFrame
    df = pd.DataFrame([data.dict()])

    # Align features with training
    df = df.reindex(columns=FEATURES, fill_value=0)

    # Predict
    prediction = model.predict(df)

    return {
        "prediction": float(prediction[0])
    }


##Predictive Maintenance
import os
import joblib
import numpy as np

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load PdM features
pdm_features = joblib.load(
    os.path.join(
        BASE_DIR,
        "phase_2_predictive_maintenance",
        "models",
        "pdm_features.pkl"
    )
)

# Load PdM model
pdm_model = joblib.load(
    os.path.join(
        BASE_DIR,
        "phase_2_predictive_maintenance",
        "models",
        "pdm_isolation_forest.pkl"
    )
)

from pydantic import BaseModel

class PdMInput(BaseModel):
    DC_POWER: float
    AC_POWER: float
    ac_lag_1: float
    ac_lag_24: float
    dc_lag_1: float
    dc_lag_24: float
    ac_roll_mean_6: float
    dc_roll_mean_6: float
    
    
@app.post("/detect-anomaly")
def detect_anomaly(data: PdMInput):

    # 🔴 Rule-based safety check (industry standard)
    if data.DC_POWER > 3000 and data.AC_POWER < 100:
        return {
            "status": "Abnormal behavior detected",
            "action": "Check inverter / system health (rule-based)"
        }

    # 🧠 ML-based anomaly detection
    X = np.array([[getattr(data, feature) for feature in pdm_features]])
    prediction = pdm_model.predict(X)[0]

    if prediction == -1:
        return {
            "status": "Abnormal behavior detected",
            "action": "Check inverter / system health (ML-based)"
        }
    else:
        return {
            "status": "Normal operation",
            "action": "No action required"
        }

class OptimizationInput(BaseModel):
    AC_POWER: float
    expected_ac_power: float
    DC_POWER: float

@app.post("/optimize-yield")
def optimize_yield(data: OptimizationInput):

    # Energy loss calculation
    energy_loss = data.expected_ac_power - data.AC_POWER

    # PdM fault check (same logic as Phase 2)
    pdm_fault = (data.DC_POWER > 3000) and (data.AC_POWER < 100)

    # Optimization logic
    if pdm_fault:
        return {
            "status": "Maintenance issue detected",
            "action": "Fix system before optimization"
        }

    if energy_loss > 200:   # heuristic threshold
        return {
            "status": "Energy loss detected",
            "action": "Panel cleaning recommended"
        }

    return {
        "status": "Optimal performance",
        "action": "No action required"
    }

