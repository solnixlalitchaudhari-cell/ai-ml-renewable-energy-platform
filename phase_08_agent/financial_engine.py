"""
Phase 8 — Financial Engine

Estimates financial risk (in ₹) based on model metrics.
Simulation-aware: reacts to R2, drift, MAE, RMSE, and improvement.
"""


def estimate_financial_risk(metrics):
    # --- Resolve metric values (simulation-aware) ---
    r2 = metrics.get("r2", metrics.get("metrics", {}).get("r2", 1.0))
    drift = metrics.get("drift_risk", "LOW")
    mae = metrics.get("mae", metrics.get("metrics", {}).get("mae", 0))
    rmse = metrics.get("metrics", {}).get("rmse", 0)
    improvement = metrics.get("metrics", {}).get("improvement_percent", 100)

    estimated_loss = 0

    # --- R2 degradation risk ---
    if r2 < 0.85:
        estimated_loss += 500000   # Critical model failure
    elif r2 < 0.90:
        estimated_loss += 200000   # Significant degradation
    elif r2 < 0.95:
        estimated_loss += 50000    # Minor concern

    # --- Drift risk ---
    if drift == "HIGH":
        estimated_loss += 150000
    elif drift == "MEDIUM":
        estimated_loss += 50000

    # --- MAE risk ---
    if mae > 5:
        estimated_loss += 300000
    elif mae > 3:
        estimated_loss += 100000

    # --- RMSE risk ---
    if rmse > 20:
        estimated_loss += 300000
    elif rmse > 10:
        estimated_loss += 100000

    # --- Improvement risk ---
    if improvement < 20:
        estimated_loss += 500000

    return estimated_loss
