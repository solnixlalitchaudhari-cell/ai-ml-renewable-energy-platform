"""
Phase 9 — Confidence Engine Module

Generates a confidence score (0.0 – 1.0) based on
agent agreement, drift status, and model health.

Fully simulation-aware: reacts to overridden R2
and drift_risk values from Phase 10 simulator.
"""


def compute_confidence(agent_results: dict, drift_status: dict, metrics: dict) -> dict:
    """
    Calculate confidence score based on multi-agent outputs.

    Args:
        agent_results: Combined outputs from all activated agents.
        drift_status: Drift detection result.
        metrics: Model evaluation metrics (may contain simulation overrides).

    Returns:
        dict with confidence_score (float) and breakdown.
    """
    score = 1.0
    breakdown = []

    # --- Determine R2 value ---
    # Phase 10 simulator sets top-level "r2"
    # Real metrics store it under "metrics" → "r2"
    r2 = metrics.get("r2", metrics.get("metrics", {}).get("r2", 1.0))

    # --- Determine drift risk ---
    # Phase 10 simulator sets top-level "drift_risk"
    # Also check drift_status dict from tools
    drift = metrics.get("drift_risk", drift_status.get("drift_risk", "LOW"))

    # --- Factor 1: R2 Model Health ---
    if r2 < 0.85:
        score -= 0.4
        breakdown.append(f"R2={r2}: below 0.85 threshold, -0.40")
    elif r2 < 0.90:
        score -= 0.25
        breakdown.append(f"R2={r2}: below 0.90, -0.25")
    elif r2 < 0.95:
        score -= 0.1
        breakdown.append(f"R2={r2}: below 0.95, -0.10")
    else:
        breakdown.append(f"R2={r2}: excellent, no penalty")

    # --- Factor 2: Drift Status ---
    if drift == "HIGH":
        score -= 0.4
        breakdown.append("Drift risk HIGH: -0.40")
    elif drift == "MEDIUM":
        score -= 0.15
        breakdown.append("Drift risk MEDIUM: -0.15")
    else:
        breakdown.append("Drift risk LOW: no penalty")

    # --- Factor 3: Agent Agreement ---
    risk_signals = []

    ops = agent_results.get("ops_analysis", {})
    if ops.get("operational_risk") == "High":
        risk_signals.append("ops_agent")

    finance = agent_results.get("finance_analysis", {})
    if finance.get("financial_risk") == "High":
        risk_signals.append("finance_agent")

    risk_level = agent_results.get("risk_assessment", {}).get("risk_level", "LOW")
    if risk_level == "HIGH":
        risk_signals.append("risk_agent")

    if len(risk_signals) >= 2:
        score -= 0.15
        breakdown.append(f"Multiple agents flagged risk ({', '.join(risk_signals)}): -0.15")
    elif len(risk_signals) == 1:
        score -= 0.05
        breakdown.append(f"Single agent flagged risk ({risk_signals[0]}): -0.05")
    else:
        breakdown.append("All agents agree: no risk penalty")

    # Clamp between 0.0 and 1.0
    score = round(max(0.0, min(1.0, score)), 2)

    return {
        "confidence_score": score,
        "confidence_label": _label(score),
        "breakdown": breakdown,
        "disagreeing_agents": risk_signals
    }


def _label(score: float) -> str:
    """Convert numeric score to human-readable label."""
    if score >= 0.85:
        return "HIGH"
    elif score >= 0.65:
        return "MEDIUM"
    else:
        return "LOW"
