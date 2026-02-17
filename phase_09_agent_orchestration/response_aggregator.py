"""
Phase 9 — Response Aggregator Module

Merges outputs from multiple agents into a single,
clean, structured JSON response. Prioritizes executive
summary and removes redundancy.
"""


def aggregate_responses(
    agent_results: dict,
    intent_info: dict,
    confidence: dict,
    is_simulation: bool = False
) -> dict:
    """
    Merge all agent outputs into a structured final response.

    Args:
        agent_results: Raw outputs from all activated agents.
        intent_info: Intent classification metadata.
        confidence: Confidence engine output.
        is_simulation: Whether this response uses simulated metrics.

    Returns:
        Clean, structured JSON combining all results.
    """

    # --- Determine overall system status (confidence-driven) ---
    confidence_score = confidence.get("confidence_score", 1.0)

    if confidence_score < 0.4:
        final_decision = "CRITICAL — Immediate Action Required"
        priority = "P0"
    elif confidence_score < 0.7:
        final_decision = "WARNING — Monitor Closely"
        priority = "P1"
    else:
        final_decision = "STABLE — System operating normally"
        priority = "P2"

    # --- Build executive summary ---
    executive_summary = _build_executive_summary(agent_results, final_decision)

    # --- Construct final output ---
    response = {
        "orchestration_metadata": {
            "selected_agents": intent_info.get("selected_agents", []),
            "routing_type": intent_info.get("routing_type", "unknown"),
            "orchestration_type": "intent_based",
            "agent_count": intent_info.get("agent_count", 0)
        },
        "simulation_mode": is_simulation,
        "confidence": {
            "score": confidence.get("confidence_score", 0.0),
            "label": confidence.get("confidence_label", "UNKNOWN"),
            "breakdown": confidence.get("breakdown", [])
        },
        "agent_outputs": {},
        "executive_summary": executive_summary,
        "final_decision": final_decision,
        "priority": priority
    }

    # --- Include only activated agent outputs ---
    selected = intent_info.get("selected_agents", [])

    if "ops_agent" in selected and "ops_analysis" in agent_results:
        response["agent_outputs"]["ops_analysis"] = agent_results["ops_analysis"]

    if "risk_agent" in selected and "risk_assessment" in agent_results:
        response["agent_outputs"]["risk_assessment"] = agent_results["risk_assessment"]

    if "finance_agent" in selected and "finance_analysis" in agent_results:
        response["agent_outputs"]["finance_analysis"] = agent_results["finance_analysis"]

    if "executive_agent" in selected:
        response["agent_outputs"]["strategy_summary"] = agent_results.get("strategy_summary", "")

    # Include drift if risk_agent was selected
    if "risk_agent" in selected and "drift_status" in agent_results:
        response["agent_outputs"]["drift_status"] = agent_results["drift_status"]

    return response


def _build_executive_summary(agent_results: dict, final_decision: str) -> str:
    """Generate a concise executive summary from agent outputs."""

    parts = []

    ops = agent_results.get("ops_analysis", {})
    if ops:
        parts.append(
            f"Operations: {ops.get('operational_risk', 'N/A')} risk — "
            f"{ops.get('reason', 'No details')}"
        )

    finance = agent_results.get("finance_analysis", {})
    if finance:
        parts.append(
            f"Finance: {finance.get('financial_risk', 'N/A')} risk — "
            f"{finance.get('impact', 'No details')}"
        )

    risk = agent_results.get("risk_assessment", {})
    if risk:
        parts.append(
            f"Risk Level: {risk.get('risk_level', 'N/A')} "
            f"(Est. Loss: ₹{risk.get('estimated_financial_risk', 0):,.0f})"
        )

    strategy = agent_results.get("strategy_summary", "")
    if strategy:
        parts.append(f"Strategy: {strategy}")

    parts.append(f"Decision: {final_decision}")

    return " | ".join(parts)
