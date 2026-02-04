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
