from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ===============================
# LOAD ENVIRONMENT VARIABLES
# ===============================
load_dotenv()

ENV = os.getenv("ENV", "development")
API_KEY = os.getenv("API_KEY")
COST_PER_KWH = float(os.getenv("COST_PER_KWH", 6.5))

if API_KEY is None:
    raise RuntimeError("API_KEY not set in environment")

# ===============================
# API KEY SECURITY
# ===============================
def verify_api_key(x_api_key: str = Header(..., alias="X-API-KEY")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# ===============================
# LOGGING
# ===============================
from phase_4_mlops.logging.logger import log_prediction

# ===============================
# SAFE DRIFT IMPORT
# ===============================
try:
    from phase_4_mlops.drift.drift_detector import check_drift
except ImportError:
    def check_drift(feature_name, value):
        return False

# ===============================
# RUNTIME STATE
# ===============================
START_TIME = datetime.utcnow()
LAST_PREDICTION_TIME = None

# ===============================
# BASE DIRECTORY
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ===============================
# LOAD MODEL METADATA
# ===============================
METADATA_PATH = os.path.join(
    BASE_DIR,
    "phase_4_mlops",
    "versioning",
    "metadata.json"
)

with open(METADATA_PATH, "r") as f:
    metadata = json.load(f)

FORECAST_MODEL_NAME = metadata["forecasting_model"]

# ===============================
# LOAD FORECASTING MODEL
# ===============================
forecast_model = joblib.load(
    os.path.join(BASE_DIR, "models", "forecasting", f"{FORECAST_MODEL_NAME}.pkl")
)

FORECAST_FEATURES = joblib.load(
    os.path.join(BASE_DIR, "models", "forecasting", "xgb_features_v1.pkl")
)

# ===============================
# LOAD PdM MODEL
# ===============================
pdm_model = joblib.load(
    os.path.join(
        BASE_DIR,
        "phase_2_predictive_maintenance",
        "models",
        "pdm_isolation_forest.pkl"
    )
)

pdm_features = joblib.load(
    os.path.join(
        BASE_DIR,
        "phase_2_predictive_maintenance",
        "models",
        "pdm_features.pkl"
    )
)

# ===============================
# FASTAPI APP
# ===============================
app = FastAPI(title="SolarOps AI Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# ROOT (UNPROTECTED)
# ===============================
@app.get("/")
def root():
    return {
        "message": "SolarOps AI Platform Running",
        "environment": ENV
    }

# ===============================
# HEALTH CHECK
# ===============================
@app.get("/health", dependencies=[Depends(verify_api_key)])
def health_check():
    return {
        "status": "healthy",
        "environment": ENV,
        "uptime_seconds": (datetime.utcnow() - START_TIME).total_seconds(),
        "forecast_model": FORECAST_MODEL_NAME,
        "forecast_model_loaded": True,
        "pdm_model_loaded": True,
        "last_prediction_time": (
            LAST_PREDICTION_TIME.isoformat()
            if LAST_PREDICTION_TIME else None
        )
    }

# ===============================
# INPUT SCHEMAS
# ===============================
class SolarInput(BaseModel):
    DC_POWER: float
    hour: int
    day: int
    month: int

class PdMInput(BaseModel):
    DC_POWER: float
    AC_POWER: float
    ac_lag_1: float
    ac_lag_24: float
    dc_lag_1: float
    dc_lag_24: float
    ac_roll_mean_6: float
    dc_roll_mean_6: float

class OptimizationInput(BaseModel):
    AC_POWER: float
    expected_ac_power: float
    DC_POWER: float

# ===============================
# PHASE 1 – FORECASTING
# ===============================
@app.post("/predict-power", dependencies=[Depends(verify_api_key)])
def predict_power(data: SolarInput):
    global LAST_PREDICTION_TIME
    LAST_PREDICTION_TIME = datetime.utcnow()

    df = pd.DataFrame([data.dict()])
    df = df.reindex(columns=FORECAST_FEATURES, fill_value=0)

    prediction = forecast_model.predict(df)[0]
    drift_detected = check_drift("DC_POWER", data.DC_POWER)

    log_prediction(
        endpoint="predict-power",
        dc_power=data.DC_POWER,
        ac_power=None,
        prediction=float(prediction),
        status="drift_detected" if drift_detected else "success",
        model_version=FORECAST_MODEL_NAME
    )

    return {
        "prediction": float(prediction),
        "drift_detected": drift_detected
    }

# ===============================
# PHASE 2 – PREDICTIVE MAINTENANCE
# ===============================
@app.post("/detect-anomaly", dependencies=[Depends(verify_api_key)])
def detect_anomaly(data: PdMInput):
    global LAST_PREDICTION_TIME
    LAST_PREDICTION_TIME = datetime.utcnow()

    if data.DC_POWER > 3000 and data.AC_POWER < 100:
        prediction = -1
        status = "abnormal_rule"
    else:
        X = pd.DataFrame(
            [[getattr(data, f) for f in pdm_features]],
            columns=pdm_features
        )
        prediction = pdm_model.predict(X)[0]
        status = "abnormal_ml" if prediction == -1 else "normal"

    log_prediction(
        endpoint="detect-anomaly",
        dc_power=data.DC_POWER,
        ac_power=data.AC_POWER,
        prediction=int(prediction),
        status=status,
        model_version="isolation_forest_v1"
    )

    return {
        "status": "Abnormal" if prediction == -1 else "Normal",
        "action": "Check inverter / system health" if prediction == -1 else "No action required"
    }

# ===============================
# PHASE 3 – OPTIMIZATION
# ===============================
@app.post("/optimize-yield", dependencies=[Depends(verify_api_key)])
def optimize_yield(data: OptimizationInput):
    global LAST_PREDICTION_TIME
    LAST_PREDICTION_TIME = datetime.utcnow()

    energy_loss = max(0, data.expected_ac_power - data.AC_POWER)

    status = "optimal"
    action = "No action required"

    if energy_loss > 200:
        status = "energy_loss"
        action = "Panel cleaning recommended"

    log_prediction(
        endpoint="optimize-yield",
        dc_power=data.DC_POWER,
        ac_power=data.AC_POWER,
        prediction=energy_loss,
        status=status,
        model_version="rule_v1"
    )

    return {
        "status": status,
        "action": action
    }

# ===============================
# PHASE 5 – BUSINESS IMPACT
# ===============================
@app.post("/business-impact", dependencies=[Depends(verify_api_key)])
def business_impact(data: OptimizationInput):
    global LAST_PREDICTION_TIME
    LAST_PREDICTION_TIME = datetime.utcnow()

    energy_loss_kwh = max(0, data.expected_ac_power - data.AC_POWER)

    hourly_loss = energy_loss_kwh * COST_PER_KWH
    daily_loss = hourly_loss * 10
    annual_loss = daily_loss * 365

    if annual_loss > 500000:
        roi_level = "CRITICAL"
        recommendation = "Immediate maintenance required"
    elif annual_loss > 200000:
        roi_level = "HIGH"
        recommendation = "Schedule optimization within 7 days"
    elif annual_loss > 50000:
        roi_level = "MODERATE"
        recommendation = "Monitor system performance"
    else:
        roi_level = "LOW"
        recommendation = "System operating efficiently"

    log_prediction(
        endpoint="business-impact",
        dc_power=data.DC_POWER,
        ac_power=data.AC_POWER,
        prediction=annual_loss,
        status=roi_level.lower(),
        model_version="phase_5_business_logic_v1"
    )

    return {
        "financial_summary": {
            "hourly_loss_rupees": round(hourly_loss, 2),
            "daily_loss_rupees": round(daily_loss, 2),
            "annual_loss_rupees": round(annual_loss, 2)
        },
        "roi_assessment": roi_level,
        "executive_recommendation": recommendation,
        "cost_per_kwh_used": COST_PER_KWH
    }
