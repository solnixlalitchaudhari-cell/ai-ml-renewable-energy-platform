import pandas as pd
import numpy as np
import os
import joblib

# ===============================
# PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "solar_features.csv")
BASE_MODEL_PATH = os.path.join(BASE_DIR, "models", "forecasting", "xgb_base_model.pkl")

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv(DATA_PATH)
df = df.select_dtypes(include=[np.number])

# ===============================
# ADD plant_id (Simulation)
# ===============================
if "plant_id" not in df.columns:
    np.random.seed(42)
    df["plant_id"] = np.random.choice([1, 2], size=len(df))

TARGET = "AC_POWER"
PLANT_ID = 1   # Change this to fine-tune different plant

# ===============================
# FILTER PLANT DATA
# ===============================
plant_df = df[df["plant_id"] == PLANT_ID]

X = plant_df.drop(columns=[TARGET])
y = plant_df[TARGET]

split_index = int(len(plant_df) * 0.8)

X_train = X.iloc[:split_index]
y_train = y.iloc[:split_index]

# ===============================
# LOAD BASE MODEL
# ===============================
model = joblib.load(BASE_MODEL_PATH)

# ===============================
# FINE-TUNE (Continue Training)
# ===============================
model.fit(X_train, y_train)

# ===============================
# SAVE FINE-TUNED MODEL
# ===============================
FT_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "forecasting",
    f"xgb_plant_{PLANT_ID}_ft.pkl"
)

joblib.dump(model, FT_MODEL_PATH)

print(f"Fine-tuned model for plant {PLANT_ID} saved successfully.")
