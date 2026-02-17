"""
Phase 8 — Finance Agent

Evaluates financial risk based on model metrics.
Simulation-aware: reacts to R2, drift, MAE, and improvement.
"""


def finance_analysis(metrics):
    r2 = metrics.get("r2", metrics.get("metrics", {}).get("r2", 1.0))
    drift = metrics.get("drift_risk", "LOW")
    mae = metrics.get("mae", metrics.get("metrics", {}).get("mae", 0))
    improvement = metrics.get("metrics", {}).get("improvement_percent", 100)

    # --- Determine financial risk level ---
    if r2 < 0.85 or (drift == "HIGH" and r2 < 0.90) or improvement < 20:
        return {
            "financial_risk": "High",
            "impact": "Significant revenue deviation risk — model accuracy critically degraded"
        }

    if r2 < 0.90 or drift == "HIGH" or mae > 5:
        return {
            "financial_risk": "Medium",
            "impact": "Moderate revenue risk — model performance below optimal"
        }

    return {
        "financial_risk": "Low",
        "impact": "Forecasting aligned with revenue targets"
    }
