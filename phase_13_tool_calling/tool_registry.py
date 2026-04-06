"""
Phase 13 — Tool Registry

Maps tool names to their execution functions.
Central source of truth for available tools.
"""

from phase_08_agent.ops_agent import ops_analysis
from phase_08_agent.finance_agent import finance_analysis
from phase_08_agent.strategy_agent import strategy_recommendation
from phase_08_agent.risk_engine import calculate_risk
from phase_08_agent.financial_engine import estimate_financial_risk
from phase_09_agent_orchestration.tools import get_drift_status, get_recent_logs
from phase_09_agent_orchestration.scenario_engine import simulate_metrics, simulate_drift

from phase_13_tool_calling.schemas import (
    RiskAssessmentOutput,
    OpsAnalysisOutput,
    FinanceAnalysisOutput,
    StrategySummaryOutput,
    DriftStatusOutput,
    SimulationOutput
)

# Wrapper for risk agent to match standard signature
def run_risk_agent(shared_state: dict) -> dict:
    metrics = shared_state.get("metrics", {})
    return {
        "risk_assessment": {
            "risk_level": calculate_risk(metrics),
            "estimated_financial_risk": estimate_financial_risk(metrics)
        }
    }

def run_ops_agent(shared_state: dict) -> dict:
    metrics = shared_state.get("metrics", {})
    return {"ops_analysis": ops_analysis(metrics)}

def run_finance_agent(shared_state: dict) -> dict:
    metrics = shared_state.get("metrics", {})
    return {"finance_analysis": finance_analysis(metrics)}

def run_strategy_agent(shared_state: dict) -> dict:
    metrics = shared_state.get("metrics", {})
    return {"strategy_summary": strategy_recommendation(metrics)}

def check_drift_status(shared_state: dict) -> dict:
    # ignores metrics input, fetches explicitly
    return {"drift_status": get_drift_status()}

def fetch_recent_logs(shared_state: dict) -> dict:
    return {"recent_logs": get_recent_logs(limit=5)}

def run_simulation(shared_state: dict) -> dict:
    """Wrapper for simulation engine."""
    question = shared_state.get("question", "")
    metrics = shared_state.get("metrics", {})
    args = shared_state.get("args", {}) # explicit overrides from planner
    
    # Run simulation
    # 1. Start with Regex based simulation (implicit)
    simulated_metrics = simulate_metrics(question, metrics)
    simulated_drift = simulate_drift(question, shared_state.get("drift_status", {}))
    
    # 2. Apply explicit overrides from Planner (Level 3)
    if "overrides" in args:
        overrides = args["overrides"]
        if "metrics" not in simulated_metrics:
            simulated_metrics["metrics"] = {}
            
        # Merge overrides
        for key, val in overrides.items():
            # Handle flattened vs nested
            if key in ["r2", "rmse", "mape", "mae"]:
                simulated_metrics["metrics"][key] = val
            elif key == "financial_risk":
                # Special handling for financial override (if needed downstream)
                # But typically financial agents re-evaluate
                pass 
                
        print(f"   ⚡ Applied Parameter Overrides: {overrides}")
    
    # 3. Update the shared state directly so subsequent tools use these values!
    shared_state["metrics"] = simulated_metrics
    shared_state["drift_status"] = simulated_drift
    shared_state["overrides_applied"] = args.get("overrides", {})
    
    return {
        "simulation_result": {
            "metrics": simulated_metrics,
            "drift_status": simulated_drift,
            "is_simulation": True
        }
    }


TOOL_REGISTRY = {
    "ops_agent": {
        "func": run_ops_agent,
        "desc": "Analyzes operational metrics (RMSE, R2) to detect performance issues.",
        "schema": OpsAnalysisOutput
    },
    "risk_agent": {
        "func": run_risk_agent,
        "desc": "Calcuates overall risk level and estimated financial loss.",
        "schema": RiskAssessmentOutput
    },
    "finance_agent": {
        "func": run_finance_agent,
        "desc": "Evaluates financial implications of model performance.",
        "schema": FinanceAnalysisOutput
    },
    "strategy_agent": {
        "func": run_strategy_agent,
        "desc": "Provides executive strategic recommendations.",
        "schema": StrategySummaryOutput
    },
    "drift_checker": {
        "func": check_drift_status,
        "desc": "Checks for data drift and model degradation.",
        "schema": DriftStatusOutput
    },
    "log_inspector": {
        "func": fetch_recent_logs,
        "desc": "Retrieves recent prediction logs for debugging.",
        "schema": None # No strict schema for logs right now
    },
    "simulation_engine": {
        "func": run_simulation,
        "desc": "Simulates hypothetical scenarios by modifying metrics based on user query.",
        "schema": SimulationOutput
    }
}
