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
from phase_09_agent_orchestration.intent_classifier import classify_intent
from phase_09_agent_orchestration.confidence_engine import compute_confidence
from phase_09_agent_orchestration.response_aggregator import aggregate_responses
from phase_09_agent_orchestration.llm_client import generate_summary
from phase_09_agent_orchestration.tools import (
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
from phase_08_agent.ops_agent import ops_analysis
from phase_08_agent.finance_agent import finance_analysis
from phase_08_agent.strategy_agent import strategy_recommendation
from phase_08_agent.risk_engine import calculate_risk
from phase_08_agent.financial_engine import estimate_financial_risk
from phase_08_agent.alert_system import log_alert
from phase_08_agent.memory import add_memory
from phase_08_agent.historical_agent import historical_analysis


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
    "memory_agent": None,  # Handled via dedicated knowledge_lookup path
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
    # FAST PATH — Knowledge Lookup (Historical Queries)
    # ============================
    if intent_info["routing_type"] == "knowledge_lookup":
        hist_result = historical_analysis(question, plant_id=plant_id)

        # Generate LLM summary from historical data
        hist_data = hist_result.get("historical_analysis", {})
        summary_prompt = (
            f"Question: {question}\n\n"
            f"Historical Alert Data: {json.dumps(hist_data.get('matching_alerts', []), indent=2)}\n"
            f"Alert Statistics: {json.dumps(hist_data.get('alert_statistics', {}), indent=2)}\n"
            f"RAG Context: {hist_data.get('rag_context', 'None')}\n\n"
            f"Provide a precise answer based ONLY on the historical data above."
        )
        ai_summary = generate_summary(summary_prompt)

        # Store memory
        add_memory({
            "plant_id": plant_id,
            "question": question,
            "response": ai_summary,
            "risk_level": "HISTORICAL_LOOKUP",
            "agents_used": ["memory_agent"],
            "confidence": 0.95,
            "timestamp": started_at
        })

        return {
            "routing": intent_info,
            "executive_summary": hist_data.get("executive_summary", ""),
            "historical_data": hist_data.get("matching_alerts", []),
            "alert_statistics": hist_data.get("alert_statistics", {}),
            "rag_context": hist_data.get("rag_context", ""),
            "ai_summary": ai_summary,
            "orchestration_metadata": {
                "routing_type": "knowledge_lookup",
                "agents_used": ["memory_agent"],
                "started_at": started_at,
                "completed_at": datetime.utcnow().isoformat(),
            }
        }

    # ============================
    # STEP 2 — Phase 13 Dynamic Orchestration
    # ============================
    # Delegate to LLM Planner for all reasoning tasks
    from phase_13_tool_calling.tool_router import run_dynamic_orchestration
    
    dynamic_result = run_dynamic_orchestration(question, plant_id)
    
    # ============================
    # STEP 3 — Wrap & Format Output
    # ============================
    # We must adapt Phase 13 output to match existing API schema
    
    # Extract data from dynamic result
    tool_results = dynamic_result.get("tool_results", {})
    plan = dynamic_result.get("plan", {})
    final_answer = dynamic_result.get("final_answer", "")
    metadata = dynamic_result.get("metadata", {})
    
    # Map to legacy structure
    response = {
        "orchestration_type": "llm_dynamic_planning",
        "question": question,
        "final_decision": "Analysis Complete", # Placeholder
        "priority": "P2", # Default, needs real logic if alert not triggered
        "executive_summary": final_answer,
        "agent_outputs": tool_results,
        "confidence": {
            "score": 1.0, # Phase 13 assumes high confidence if plan succeeds
            "label": "HIGH",
            "breakdown": ["Dynamic planning successful"]
        },
        "orchestration_metadata": {
            "selected_agents": metadata.get("tools_used", []),
            "routing_type": "dynamic_planner",
            "started_at": metadata.get("started_at"),
            "completed_at": metadata.get("completed_at"),
            "plan": plan
        }
    }

    # ============================
    # STEP 4 — Phase 11 Alert Evaluation
    # ============================
    # Re-evaluate alerts based on the tool outputs
    
    eval_context = copy.deepcopy(response)
    
    # Use metrics from the shared_state (which correctly contains mutated simulation data!)
    shared_state = dynamic_result.get("shared_state", {})
    eval_context["metrics"] = shared_state.get("metrics", {})
    eval_context["simulation_overrides"] = shared_state.get("overrides_applied", {})

    alert_info = evaluate_alert(eval_context, plant_id)
    response["alert"] = alert_info
    
    # Update priority/decision based on alert
    response["priority"] = alert_info.get("severity", "P2")
    if alert_info.get("alert_triggered"):
        response["final_decision"] = "CRITICAL ALERT TRIGGERED"
    else:
        response["final_decision"] = "System Nominal"

    # ============================
    # STEP 5 — Store Memory
    # ============================
    risk_level = "LOW" # Default
    if "risk_assessment" in tool_results:
        risk_level = tool_results["risk_assessment"].get("risk_level", "LOW")

    add_memory({
        "plant_id": plant_id,
        "question": question,
        "response": final_answer,
        "risk_level": risk_level,
        "agents_used": metadata.get("tools_used", []),
        "confidence": 1.0,
        "timestamp": started_at
    })

    return response

