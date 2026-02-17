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
        {"severity": "P0"|"P1"|"P2", "reason": str}
    """

    decision = orchestration_result.get("final_decision", "")
    priority = orchestration_result.get("priority", "P2")
    confidence = orchestration_result.get("confidence", {})
    agent_outputs = orchestration_result.get("agent_outputs", {})

    # --- Extract key signals ---
    risk_assessment = agent_outputs.get("risk_assessment", {})
    risk_level = risk_assessment.get("risk_level", "LOW")
    estimated_loss = risk_assessment.get("estimated_financial_risk", 0)

    ops = agent_outputs.get("ops_analysis", {})
    ops_risk = ops.get("operational_risk", "Low")

    finance = agent_outputs.get("finance_analysis", {})
    finance_risk = finance.get("financial_risk", "Low")

    drift_status = agent_outputs.get("drift_status", {})
    drift_risk = drift_status.get("drift_risk", "LOW")

    conf_label = confidence.get("label", "HIGH")

    # Simulation risk (from Phase 10)
    sim_risk = agent_outputs.get("simulation_risk", {})
    sim_risk_level = sim_risk.get("risk_level", "LOW")
    sim_financial = sim_risk.get("estimated_financial_risk", 0)

    # --- P0: CRITICAL ---
    if "CRITICAL" in decision.upper():
        return {"severity": "P0", "reason": f"Final decision is CRITICAL: {decision}"}

    if estimated_loss >= 500000 or sim_financial >= 500000:
        loss = max(estimated_loss, sim_financial)
        return {"severity": "P0", "reason": f"Estimated financial risk ₹{loss:,} exceeds ₹500,000 threshold"}

    if risk_level == "CRITICAL" or sim_risk_level == "CRITICAL":
        return {"severity": "P0", "reason": "Risk assessment is CRITICAL"}

    if drift_risk == "HIGH":
        # Check for R2 in simulation_risk or agent outputs
        sim_r2 = sim_risk.get("risk_factors", [])
        r2_critical = any("below 0.85" in f for f in sim_r2)
        if r2_critical:
            return {"severity": "P0", "reason": "Drift HIGH and R2 below 0.85 threshold"}

    # --- P1: WARNING ---
    if finance_risk == "High":
        return {"severity": "P1", "reason": "Finance agent flagged HIGH financial risk"}

    if ops_risk in ("Medium", "High"):
        return {"severity": "P1", "reason": f"Operational risk is {ops_risk}"}

    if risk_level in ("HIGH", "MEDIUM"):
        return {"severity": "P1", "reason": f"Risk assessment is {risk_level}"}

    if conf_label == "LOW":
        return {"severity": "P1", "reason": "Confidence is LOW — uncertain prediction quality"}

    if priority == "P0":
        return {"severity": "P1", "reason": "Priority escalated to P0 by aggregator"}

    # --- P2: INFO ---
    return {"severity": "P2", "reason": "All systems nominal — no escalation needed"}
