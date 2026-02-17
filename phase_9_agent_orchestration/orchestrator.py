"""
Phase 9 — Intelligent Multi-Agent Orchestration

Central orchestrator that:
1. Classifies user intent
2. Selects and runs relevant agents
3. Gathers tool data (metrics, logs, drift)
4. Computes confidence score
5. Aggregates responses
6. Generates LLM summary
7. Stores memory and logs alerts
8. Returns structured JSON

Entry point: run_orchestration(plant_id, question)
"""

import json
import copy
from datetime import datetime

# --- Phase 9 Modules ---
from phase_9_agent_orchestration.intent_classifier import classify_intent
from phase_9_agent_orchestration.confidence_engine import compute_confidence
from phase_9_agent_orchestration.response_aggregator import aggregate_responses
from phase_9_agent_orchestration.llm_client import generate_summary
from phase_9_agent_orchestration.tools import (
    get_model_metrics,
    get_recent_logs,
    get_drift_status
)

# --- Phase 10 Scenario Engine (Enterprise) ---
from phase_10_scenario_engine import (
    detect_scenario,
    apply_metric_overrides,
    recalculate_risk,
    log_simulation
)

# --- Phase 11 Alerting ---
from phase_11_alerting.alert_engine import evaluate_alert

# --- Phase 8 Agents ---
from phase_8_agent.ops_agent import ops_analysis
from phase_8_agent.finance_agent import finance_analysis
from phase_8_agent.strategy_agent import strategy_recommendation
from phase_8_agent.risk_engine import calculate_risk
from phase_8_agent.financial_engine import estimate_financial_risk
from phase_8_agent.alert_system import log_alert
from phase_8_agent.memory import add_memory


# Agent registry — maps agent names to their execution functions
AGENT_REGISTRY = {
    "ops_agent": lambda metrics: {"ops_analysis": ops_analysis(metrics)},
    "risk_agent": lambda metrics: {
        "risk_assessment": {
            "risk_level": calculate_risk(metrics),
            "estimated_financial_risk": estimate_financial_risk(metrics)
        }
    },
    "finance_agent": lambda metrics: {"finance_analysis": finance_analysis(metrics)},
    "executive_agent": lambda metrics: {"strategy_summary": strategy_recommendation(metrics)},
}


def run_orchestration(plant_id: int, question: str, override_metrics=None) -> dict:
    """
    Full orchestration pipeline. This is the only function
    the FastAPI endpoint needs to call.

    Args:
        plant_id: The solar plant identifier.
        question: User's natural language question.
        override_metrics: Optional dict of simulated metrics
            from Phase 10 simulation engine. When provided,
            these replace the real metrics from tools.

    Returns:
        Structured JSON with agent outputs, confidence,
        executive summary, and LLM-generated explanation.
    """

    started_at = datetime.utcnow().isoformat()

    # ============================
    # STEP 1 — Classify Intent
    # ============================
    intent_info = classify_intent(question)
    selected_agents = intent_info["selected_agents"]

    # ============================
    # STEP 2 — Gather Tool Data
    # ============================
    if override_metrics:
        metrics = override_metrics
    else:
        metrics = get_model_metrics()
    recent_logs = get_recent_logs()
    drift_status = get_drift_status()

    # ============================
    # STEP 2.5 — Phase 10 Scenario Simulation
    # ============================
    scenario = detect_scenario(question)
    simulation_mode = scenario["is_simulation"]

    if simulation_mode:
        metrics = apply_metric_overrides(metrics, scenario["overrides"])

    # Phase 9 scenario engine (hypothetical detection)
    simulation_active = intent_info.get("is_hypothetical", False)
    if simulation_active:
        simulation_mode = True
        from phase_9_agent_orchestration.scenario_engine import simulate_metrics, simulate_drift
        real_metrics = copy.deepcopy(metrics)
        real_drift = copy.deepcopy(drift_status)
        metrics = simulate_metrics(question, metrics)
        drift_status = simulate_drift(question, drift_status)

    # ============================
    # STEP 3 — Run Selected Agents
    # ============================
    agent_results = {}

    for agent_name in selected_agents:
        if agent_name in AGENT_REGISTRY:
            result = AGENT_REGISTRY[agent_name](metrics)
            agent_results.update(result)

    # Always include drift and logs for context
    agent_results["drift_status"] = drift_status
    agent_results["recent_logs"] = recent_logs

    # ============================
    # STEP 4 — Compute Confidence
    # ============================
    confidence = compute_confidence(agent_results, drift_status, metrics)

    # ============================
    # STEP 4.5 — Recalculate Risk & Log (Simulation)
    # ============================
    if simulation_mode:
        risk_data = recalculate_risk(metrics)
        agent_results["simulation_risk"] = risk_data

        log_simulation({
            "question": question,
            "overrides": scenario["overrides"],
            "risk_result": risk_data,
            "confidence": confidence["confidence_score"]
        })

    # ============================
    # STEP 5 — Aggregate Responses
    # ============================
    aggregated = aggregate_responses(agent_results, intent_info, confidence, is_simulation=simulation_mode)

    # Add simulation metadata if hypothetical
    if simulation_active:
        aggregated["simulation"] = {
            "active": True,
            "real_metrics": real_metrics.get("metrics", {}),
            "simulated_metrics": metrics.get("metrics", {}),
            "real_drift": real_drift,
            "simulated_drift": drift_status
        }

    # ============================
    # STEP 6 — LLM Final Summary
    # ============================
    summary_prompt = (
        f"Question: {question}\n\n"
        f"Executive Summary: {aggregated.get('executive_summary', '')}\n"
        f"Final Decision: {aggregated.get('final_decision', '')}\n"
        f"Priority: {aggregated.get('priority', '')}\n"
        f"Confidence: {aggregated.get('confidence', {})}\n"
        f"Agent Outputs: {json.dumps(aggregated.get('agent_outputs', {}), indent=2)}"
    )
    ai_summary = generate_summary(summary_prompt)
    aggregated["ai_summary"] = ai_summary

    # ============================
    # STEP 7 — Phase 11 Alert Evaluation
    # ============================
    alert_info = evaluate_alert(aggregated, plant_id)
    aggregated["alert"] = alert_info

    risk_level = agent_results.get("risk_assessment", {}).get("risk_level", "LOW")

    # ============================
    # STEP 8 — Store Memory
    # ============================
    add_memory({
        "plant_id": plant_id,
        "question": question,
        "response": ai_summary,
        "risk_level": risk_level,
        "agents_used": selected_agents,
        "confidence": confidence["confidence_score"],
        "timestamp": started_at
    })

    # ============================
    # STEP 9 — Add Timing Metadata
    # ============================
    aggregated["orchestration_metadata"]["started_at"] = started_at
    aggregated["orchestration_metadata"]["completed_at"] = datetime.utcnow().isoformat()

    return aggregated

