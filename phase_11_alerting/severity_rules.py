"""
Phase 11 — Severity Rules

Evaluates orchestration output and determines alert severity.

Severity Matrix:
    P0 (CRITICAL):
        - final_decision contains "CRITICAL"
        - estimated_financial_risk >= 500,000
        - drift HIGH AND R2 < 0.85
    P1 (WARNING):
        - financial_risk == "High"
        - operational_risk == "Medium" or "High"
        - confidence label == "LOW"
    P2 (INFO):
        - Everything else
"""


def determine_severity(orchestration_result: dict) -> dict:
    """
    Determine alert severity from orchestration output.

    Args:
        orchestration_result: Full response from run_orchestration().

    Returns:
        {"severity": "P0"|"P1"|"P2", "reason": str, "context": dict}
    """

    decision = orchestration_result.get("final_decision", "")
    priority = orchestration_result.get("priority", "P2")
    confidence = orchestration_result.get("confidence", {})
    agent_outputs = orchestration_result.get("agent_outputs", {})

    # --- Extract key signals ---
    risk_assessment = agent_outputs.get("risk_assessment", {})
    risk_level = risk_assessment.get("risk_level", "LOW")
    estimated_loss = risk_assessment.get("estimated_financial_risk", 0)
    
    # Extract overrides for deterministic logic
    simulation_overrides = orchestration_result.get("simulation_overrides", {})
    override_financial = float(simulation_overrides.get("estimated_financial_risk", 0))
    max_financial_loss = max(estimated_loss, override_financial)
    
    # Extract metrics for context
    metrics = orchestration_result.get("metrics", {})
    metrics_data = metrics.get("metrics", metrics) # Ensure we handle flat or nested safely
    
    # Calculate requested context fields
    mape = metrics_data.get("mape", 0)
    r2 = metrics_data.get("r2", 1.0)
    rmse = metrics_data.get("rmse", 0)
    
    # Anomaly score derivation (inverse of R2 + RMSE factor)
    # Simple heuristic: (1 - R2) + (RMSE / 100) -> 0.0 to 1.0 scale
    anomaly_score = round(min(1.0, (1.0 - float(r2)) + (float(rmse) / 100)), 2)
    
    # Common context to be merged
    base_context = {
        "forecast_deviation_percent": float(mape),
        "anomaly_score": float(anomaly_score),
        "model_confidence": float(confidence.get("confidence_score", 0.0)),
        "triggered_rules": [],
        "metrics": metrics_data,
        "applied_overrides": simulation_overrides
    }

    ops = agent_outputs.get("ops_analysis", {})
    ops_risk = ops.get("operational_risk", "Low")

    finance = agent_outputs.get("finance_analysis", {})
    finance_risk = finance.get("financial_risk", "Low")

    drift_status = agent_outputs.get("drift_status", {})
    drift_risk = drift_status.get("drift_risk", "LOW")

    conf_label = confidence.get("label", "HIGH")

    # Simulation risk (from Phase 10 - legacy, but we keep it safe)
    sim_risk = agent_outputs.get("simulation_risk", {})
    sim_risk_level = sim_risk.get("risk_level", "LOW")
    sim_r2 = sim_risk.get("risk_factors", [])

    # --- P0: CRITICAL ---
    if "CRITICAL" in decision.upper():
        ctx = base_context.copy()
        ctx["triggered_rules"].append("final_decision_critical")
        ctx["root_cause"] = f"Final decision is CRITICAL: {decision}"
        return {
            "severity": "P0",
            "reason": ctx["root_cause"],
            "context": ctx
        }

    # DETERMINISTIC ESCALATION rule:
    if max_financial_loss >= 500000:
        ctx = base_context.copy()
        ctx["triggered_rules"].append("financial_risk_threshold_exceeded")
        ctx["estimated_financial_risk"] = estimated_loss
        ctx["override_financial_risk"] = override_financial
        ctx["threshold"] = 500000
        ctx["root_cause"] = f"Deterministic escalation: Financial risk ₹{max_financial_loss:,.2f} exceeds ₹500,000 threshold"
        return {
            "severity": "P0",
            "reason": ctx["root_cause"],
            "context": ctx
        }

    if risk_level == "CRITICAL" or sim_risk_level == "CRITICAL":
        ctx = base_context.copy()
        ctx["triggered_rules"].append("risk_level_critical")
        ctx["risk_level"] = risk_level
        ctx["simulation_risk_level"] = sim_risk_level
        ctx["root_cause"] = "Risk assessment is CRITICAL"
        return {
            "severity": "P0",
            "reason": ctx["root_cause"],
            "context": ctx
        }

    if drift_risk == "HIGH":
        # Check for R2 in simulation_risk or agent outputs
        r2_critical = any("below 0.85" in f for f in sim_r2) or float(r2) < 0.85
        if r2_critical:
            ctx = base_context.copy()
            ctx["triggered_rules"].append("drift_high_r2_low")
            ctx["drift_risk"] = drift_risk
            ctx["simulated_r2_status"] = "below_0.85"
            ctx["root_cause"] = "Drift HIGH and R2 below 0.85 threshold"
            return {
                "severity": "P0",
                "reason": ctx["root_cause"],
                "context": ctx
            }

    # --- P1: WARNING ---
    if finance_risk == "High":
        ctx = base_context.copy()
        ctx["triggered_rules"].append("finance_risk_high")
        ctx["financial_risk"] = finance_risk
        ctx["root_cause"] = "Finance agent flagged HIGH financial risk"
        return {
            "severity": "P1",
            "reason": ctx["root_cause"],
            "context": ctx
        }

    if ops_risk in ("Medium", "High"):
        ctx = base_context.copy()
        ctx["triggered_rules"].append("operational_risk_escalated")
        ctx["operational_risk"] = ops_risk
        ctx["root_cause"] = f"Operational risk is {ops_risk}"
        return {
            "severity": "P1",
            "reason": ctx["root_cause"],
            "context": ctx
        }

    if risk_level in ("HIGH", "MEDIUM"):
        ctx = base_context.copy()
        ctx["triggered_rules"].append("risk_level_elevated")
        ctx["risk_level"] = risk_level
        ctx["root_cause"] = f"Risk assessment is {risk_level}"
        return {
            "severity": "P1",
            "reason": ctx["root_cause"],
            "context": ctx
        }

    if conf_label == "LOW":
        ctx = base_context.copy()
        ctx["triggered_rules"].append("confidence_low")
        ctx["confidence_label"] = conf_label
        ctx["root_cause"] = "Confidence is LOW — uncertain prediction quality"
        return {
            "severity": "P1",
            "reason": ctx["root_cause"],
            "context": ctx
        }

    if priority == "P0":
        ctx = base_context.copy()
        ctx["triggered_rules"].append("priority_escalation")
        ctx["priority"] = priority
        ctx["root_cause"] = "Priority escalated to P0 by aggregator"
        return {
            "severity": "P1",
            "reason": ctx["root_cause"],
            "context": ctx
        }

    # --- P2: INFO ---
    ctx = base_context.copy()
    ctx["status"] = "nominal"
    return {
        "severity": "P2",
        "reason": "All systems nominal — no escalation needed",
        "context": ctx
    }
