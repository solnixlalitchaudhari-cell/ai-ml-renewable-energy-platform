from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests


# ===============================
# LOAD ENVIRONMENT VARIABLES
# ===============================
load_dotenv()

ENV = os.getenv("ENV", "development")
API_KEY = os.getenv("API_KEY")
COST_PER_KWH = float(os.getenv("COST_PER_KWH", 6.5))

if API_KEY is None:
    raise RuntimeError("API_KEY not set in environment")

HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise RuntimeError("HF_TOKEN not set in environment")


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
# BASE DIRECTORY (DOCKER SAFE)
# ===============================
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

# ===============================
# LOAD FORECAST FEATURES
# ===============================
forecast_features_path = os.path.join(
    BASE_DIR,
    "models",
    "forecasting",
    "xgb_features_v1.pkl"
)

if not os.path.exists(forecast_features_path):
    raise FileNotFoundError(f"Forecast features not found at {forecast_features_path}")

FORECAST_FEATURES = joblib.load(forecast_features_path)

# ===============================
# DYNAMIC MODEL LOADER (Multi-Site Support)
# ===============================
def load_forecast_model(plant_id: int):
    ft_model_path = os.path.join(
        BASE_DIR,
        "models",
        "forecasting",
        f"xgb_plant_{plant_id}_ft.pkl"
    )

    base_model_path = os.path.join(
        BASE_DIR,
        "models",
        "forecasting",
        "xgb_base_model.pkl"
    )

    if os.path.exists(ft_model_path):
        print(f"Loading fine-tuned model for plant {plant_id}")
        return joblib.load(ft_model_path)

    print("Loading base model")
    return joblib.load(base_model_path)

# ===============================
# LOAD PdM MODEL
# ===============================
pdm_model_path = os.path.join(
    BASE_DIR,
    "phase_2_predictive_maintenance",
    "models",
    "pdm_isolation_forest.pkl"
)

pdm_features_path = os.path.join(
    BASE_DIR,
    "phase_2_predictive_maintenance",
    "models",
    "pdm_features.pkl"
)

if not os.path.exists(pdm_model_path):
    raise FileNotFoundError(f"PdM model not found at {pdm_model_path}")

if not os.path.exists(pdm_features_path):
    raise FileNotFoundError(f"PdM features not found at {pdm_features_path}")

pdm_model = joblib.load(pdm_model_path)
pdm_features = joblib.load(pdm_features_path)

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
# ROOT
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
        "forecast_multi_site_enabled": True,
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
    plant_id: int
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
# PHASE 1 – FORECASTING (Multi-Site Enabled)
# ===============================
@app.post("/predict-power", dependencies=[Depends(verify_api_key)])
def predict_power(data: SolarInput):
    global LAST_PREDICTION_TIME
    LAST_PREDICTION_TIME = datetime.utcnow()

    model = load_forecast_model(data.plant_id)

    # Create minimal input
    df = pd.DataFrame([{
        "plant_id": data.plant_id,
        "DC_POWER": data.DC_POWER,
        "hour": data.hour,
        "day": data.day,
        "month": data.month
    }])

    # Align strictly to model features
    expected_features = model.get_booster().feature_names
    df = df.reindex(columns=expected_features, fill_value=0)

    prediction = model.predict(df)[0]
    drift_detected = check_drift("DC_POWER", data.DC_POWER)

    log_prediction(
        endpoint="predict-power",
        dc_power=data.DC_POWER,
        ac_power=None,
        prediction=float(prediction),
        status="drift_detected" if drift_detected else "success",
        model_version=f"plant_{data.plant_id}"
    )

    return {
        "plant_id": data.plant_id,
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

# ===============================
# MODEL METRICS
# ===============================

@app.get("/model-metrics", dependencies=[Depends(verify_api_key)])
def get_model_metrics():
    metrics_path = os.path.join(
        BASE_DIR,
        "phase_6_evaluation",
        "evaluation_report.json"
    )
    with open(metrics_path) as f:
        return json.load(f)

import requests

class AskAIInput(BaseModel):
    plant_id: int
    question: str


@app.post("/ask-ai", dependencies=[Depends(verify_api_key)])
def ask_ai(data: AskAIInput):

    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        return {"error": "HF_TOKEN not set in environment"}

    # ===============================
    # Load RAG Data (FULL CONTEXT)
    # ===============================
    evaluation_path = os.path.join(BASE_DIR, "phase_6_evaluation", "evaluation_report.json")
    history_path = os.path.join(BASE_DIR, "phase_6_evaluation", "metrics_history.json")
    logs_path = os.path.join(BASE_DIR, "phase_4_mlops", "logging", "prediction_logs.json")

    evaluation_data = {}
    history_data = []
    log_data = []

    if os.path.exists(evaluation_path):
        with open(evaluation_path, "r") as f:
            evaluation_data = json.load(f)

    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            history_data = json.load(f)[-3:]

    if os.path.exists(logs_path):
        with open(logs_path, "r") as f:
            log_data = json.load(f)[-5:]

    # ===============================
    # Build STRONG Structured Prompt
    # ===============================
    context = f"""
You are a Renewable Energy AI Expert.

Solar Forecasting Benchmarks:
- MAE < 2 strong
- MAPE < 5% excellent
- R2 > 0.95 high accuracy
- Improvement > 10% good
- Residual mean near 0 stable

Plant ID: {data.plant_id}

Current Model Evaluation:
{json.dumps(evaluation_data)}

Recent Performance Trend:
{json.dumps(history_data)}

Recent Operational Logs:
{json.dumps(log_data)}

User Question:
{data.question}

CRITICAL INSTRUCTIONS:
- Return ONLY pure JSON.
- Do NOT use markdown.
- Do NOT wrap in ```json.
- Do NOT explain outside JSON.
- Keep response under 500 tokens.
- Make executive summary concise and readable.

Required JSON format:

{{
  "executive_summary": "short 5-7 lines paragraph",
  "model_health": "Stable / Degrading / Critical",
  "drift_risk": "Low / Medium / High",
  "operational_risk": "Low / Medium / High",
  "financial_impact": "short 3-4 lines",
  "recommended_action": "short 3-4 lines",
  "confidence_level": "Low / Medium / High"
}}
"""

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "messages": [
            {
                "role": "system",
                "content": "You always return valid JSON only. No markdown. No explanation outside JSON."
            },
            {
                "role": "user",
                "content": context
            }
        ],
        "max_tokens": 500,
        "temperature": 0.2
    }

    try:
        response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90
        )

        if response.status_code != 200:
            return {
                "error": "LLM request failed",
                "status_code": response.status_code,
                "details": response.text
            }

        result = response.json()
        raw_text = result["choices"][0]["message"]["content"].strip()

        # Remove accidental markdown if model still adds it
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        ai_output = json.loads(raw_text)

    except Exception as e:
        return {
            "error": "LLM parsing failed",
            "details": str(e)
        }

    return {
        "plant_id": data.plant_id,
        "question": data.question,
        "ai_response": ai_output
    }
