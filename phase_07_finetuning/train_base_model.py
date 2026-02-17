import pandas as pd
import numpy as np
import os
import joblib
from xgboost import XGBRegressor

# ===============================
# PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "solar_features.csv")

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv(DATA_PATH)
df = df.select_dtypes(include=[np.number])

# ===============================
# ADD plant_id (Simulation for Multi-Site)
# ===============================
if "plant_id" not in df.columns:
    np.random.seed(42)
    df["plant_id"] = np.random.choice([1, 2], size=len(df))

# ===============================
# TARGET
# ===============================
TARGET = "AC_POWER"

X = df.drop(columns=[TARGET])
y = df[TARGET]

# ===============================
# TRAIN / TEST SPLIT
# ===============================
split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
y_train = y.iloc[:split_index]

# ===============================
# TRAIN BASE MODEL
# ===============================
model = XGBRegressor(n_estimators=200, max_depth=6)
model.fit(X_train, y_train)

# ===============================
# SAVE BASE MODEL
# ===============================
MODEL_PATH = os.path.join(BASE_DIR, "models", "forecasting", "xgb_base_model.pkl")
joblib.dump(model, MODEL_PATH)

print("Base model trained and saved successfully.")
