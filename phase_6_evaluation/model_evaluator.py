import pandas as pd
import numpy as np
import joblib
import os
import json
from datetime import datetime, timezone
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# ===============================
# BASE DIRECTORY
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ===============================
# LOAD DATASET
# ===============================
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "solar_features.csv")
df = pd.read_csv(DATA_PATH)

# Keep numeric columns only
df = df.select_dtypes(include=[np.number])

TARGET_COLUMN = "AC_POWER"

if TARGET_COLUMN not in df.columns:
    raise ValueError("AC_POWER column not found")

X = df.drop(columns=[TARGET_COLUMN])
y = df[TARGET_COLUMN]

# ===============================
# TIME-SERIES SPLIT (INDUSTRY STANDARD)
# ===============================
split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test  = X.iloc[split_index:]
y_train = y.iloc[:split_index]
y_test  = y.iloc[split_index:]

# ===============================
# LOAD MODEL
# ===============================
MODEL_PATH = os.path.join(BASE_DIR, "models", "forecasting", "xgb_v1.pkl")
model = joblib.load(MODEL_PATH)

# ===============================
# MODEL PREDICTIONS
# ===============================
predictions = model.predict(X_test)

# ===============================
# BASELINE (Naive Lag-1 Model)
# ===============================
if "ac_lag_1" in X_test.columns:
    baseline_pred = X_test["ac_lag_1"]
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))
else:
    baseline_rmse = None

# ===============================
# METRICS
# ===============================
mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, predictions)

# Safe MAPE (ignore zero targets)
non_zero_mask = y_test != 0
mape = np.mean(
    np.abs((y_test[non_zero_mask] - predictions[non_zero_mask]) /
           y_test[non_zero_mask])
) * 100

# Improvement %
if baseline_rmse:
    improvement = ((baseline_rmse - rmse) / baseline_rmse) * 100
else:
    improvement = None

# ===============================
# RESIDUAL ANALYSIS
# ===============================
residuals = y_test - predictions
mean_residual = np.mean(residuals)
std_residual = np.std(residuals)

# ===============================
# FEATURE IMPORTANCE
# ===============================
feature_importance = dict(zip(X.columns, model.feature_importances_))
sorted_importance = dict(
    sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
)

# ===============================
# MODEL APPROVAL LOGIC
# ===============================
if improvement and improvement > 5 and r2 > 0.95:
    model_status = "APPROVED"
else:
    model_status = "REVIEW_REQUIRED"

# ===============================
# PRINT RESULTS
# ===============================
print("\nModel Evaluation Results")
print("------------------------------------")
print(f"MAE              : {mae}")
print(f"RMSE             : {rmse}")
print(f"R2               : {r2}")
print(f"MAPE             : {mape}%")

if baseline_rmse:
    print(f"Baseline RMSE    : {baseline_rmse}")
    print(f"Improvement %    : {improvement}%")

print("\nResidual Stats")
print(f"Mean Residual    : {mean_residual}")
print(f"Std Residual     : {std_residual}")

print(f"\nModel Status     : {model_status}")

print("\nTop 5 Important Features:")
for k, v in list(sorted_importance.items())[:5]:
    print(f"{k} : {v}")

# ===============================
# BUILD REPORT
# ===============================
report = {
    "model_version": "xgb_v1",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "metrics": {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "mape": float(mape),
        "baseline_rmse": float(baseline_rmse) if baseline_rmse else None,
        "improvement_percent": float(improvement) if improvement else None
    },
    "residual_stats": {
        "mean_residual": float(mean_residual),
        "std_residual": float(std_residual)
    },
    "model_status": model_status,
    "top_features": {
        k: float(v) for k, v in list(sorted_importance.items())[:10]
    },
    "data_summary": {
        "train_size": len(X_train),
        "test_size": len(X_test),
        "feature_count": X.shape[1]
    }
}

# ===============================
# SAVE LATEST REPORT
# ===============================
REPORT_PATH = os.path.join(BASE_DIR, "phase_6_evaluation", "evaluation_report.json")

with open(REPORT_PATH, "w") as f:
    json.dump(report, f, indent=4)

# ===============================
# APPEND TO METRICS HISTORY
# ===============================
HISTORY_PATH = os.path.join(BASE_DIR, "phase_6_evaluation", "metrics_history.json")

if os.path.exists(HISTORY_PATH):
    with open(HISTORY_PATH, "r") as f:
        history = json.load(f)
else:
    history = []

history.append(report)

with open(HISTORY_PATH, "w") as f:
    json.dump(history, f, indent=4)

print("\nEvaluation report saved successfully.")
print("Evaluation history updated successfully.")
