"""
Phase 8 — Risk Engine

Calculates overall risk level based on model metrics.
Simulation-aware: reacts to R2, drift, MAPE, RMSE, and improvement.
"""


def calculate_risk(metrics):
    risk_score = 0

    # --- R2 score (simulation-aware) ---
    # Check top-level r2 first (set by Phase 10 simulator),
    # then fall back to nested metrics.r2
    r2 = metrics.get("r2", metrics.get("metrics", {}).get("r2", 1.0))

    if r2 < 0.85:
        risk_score += 4   # CRITICAL threshold
    elif r2 < 0.90:
        risk_score += 3   # HIGH threshold
    elif r2 < 0.95:
        risk_score += 1   # Minor concern

    # --- Drift risk (simulation-aware) ---
    drift = metrics.get("drift_risk", "LOW")
    if drift == "HIGH":
        risk_score += 3
    elif drift == "MEDIUM":
        risk_score += 1

    # --- MAPE ---
    if metrics.get("metrics", {}).get("mape", 0) > 5:
        risk_score += 2

    # --- RMSE ---
    if metrics.get("metrics", {}).get("rmse", 0) > 10:
        risk_score += 2

    # --- Improvement Percent ---
    if metrics.get("metrics", {}).get("improvement_percent", 100) < 20:
        risk_score += 3

    # --- Determine risk level ---
    if risk_score >= 7:
        return "CRITICAL"
    elif risk_score >= 5:
        return "HIGH"
    elif risk_score >= 3:
        return "MEDIUM"
    else:
        return "LOW"
