"""
Phase 10 — Risk Recalculator

Recalculates risk level, priority, and estimated financial impact
based on modified (simulated) metrics.

Risk Matrix:
    R2 < 0.85              → CRITICAL / P0
    R2 < 0.90              → HIGH / P1
    Drift HIGH             → escalate one level
    MAE > 3                → increase financial risk

No global state. No side effects. Pure functional logic.
"""


def recalculate_risk(metrics: dict) -> dict:
    """
    Recalculate risk from modified metrics.

    Args:
        metrics: Modified metrics dict (after overrides applied).

    Returns:
        {
            "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
            "priority": "P0" | "P1" | "P2",
            "estimated_financial_risk": int,
            "risk_factors": list[str]
        }
    """
    # --- Extract values ---
    r2 = metrics.get("r2", metrics.get("metrics", {}).get("r2", 1.0))
    drift = metrics.get("drift_risk", "LOW")
    mae = metrics.get("mae", metrics.get("metrics", {}).get("mae", 0.0))

    risk_level = "LOW"
    priority = "P2"
    financial_risk = 0
    risk_factors = []

    # --- R2 risk assessment ---
    if r2 < 0.85:
        risk_level = "CRITICAL"
        priority = "P0"
        financial_risk += 500000
        risk_factors.append(f"R2={r2} is below 0.85 (CRITICAL threshold)")
    elif r2 < 0.90:
        risk_level = "HIGH"
        priority = "P1"
        financial_risk += 200000
        risk_factors.append(f"R2={r2} is below 0.90 (HIGH threshold)")
    elif r2 < 0.95:
        risk_level = "MEDIUM"
        priority = "P1"
        financial_risk += 50000
        risk_factors.append(f"R2={r2} is below 0.95 (MEDIUM threshold)")
    else:
        risk_factors.append(f"R2={r2} is healthy")

    # --- Drift risk escalation ---
    if drift == "HIGH":
        if risk_level in ("LOW", "MEDIUM"):
            risk_level = "HIGH"
        if priority == "P2":
            priority = "P1"
        financial_risk += 150000
        risk_factors.append("Drift is HIGH — risk escalated")
    elif drift == "MEDIUM":
        if risk_level == "LOW":
            risk_level = "MEDIUM"
        financial_risk += 50000
        risk_factors.append("Drift is MEDIUM — moderate concern")
    else:
        risk_factors.append("Drift is LOW — no escalation")

    # --- MAE risk factor ---
    if mae > 5:
        financial_risk += 300000
        risk_factors.append(f"MAE={mae} is critically high (>5)")
    elif mae > 3:
        financial_risk += 100000
        risk_factors.append(f"MAE={mae} is elevated (>3)")
    else:
        risk_factors.append(f"MAE={mae} is acceptable")

    return {
        "risk_level": risk_level,
        "priority": priority,
        "estimated_financial_risk": financial_risk,
        "risk_factors": risk_factors
    }
