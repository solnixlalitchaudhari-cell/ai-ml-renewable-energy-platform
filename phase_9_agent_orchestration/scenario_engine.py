"""
Phase 10 — Scenario Simulation Engine

Detects hypothetical questions and creates simulated metrics
by parsing threshold values from user questions.

Transforms the system from reactive (state-based) to
strategic (scenario reasoning).
"""

import re
import copy


# Keywords that indicate a hypothetical question
HYPOTHETICAL_KEYWORDS = [
    "what if", "what happens", "suppose", "imagine",
    "assume", "hypothetical", "scenario", "simulate",
    "drops below", "drops to", "falls to", "falls below",
    "increases to", "rises to", "becomes"
]


def is_hypothetical(question: str) -> bool:
    """
    Detect if a question is asking about a hypothetical scenario.

    Args:
        question: User's natural language question.

    Returns:
        True if the question is hypothetical.
    """
    question_lower = question.lower()
    return any(kw in question_lower for kw in HYPOTHETICAL_KEYWORDS)


def simulate_metrics(question: str, real_metrics: dict) -> dict:
    """
    Parse the user's question for threshold values and create
    a simulated copy of the metrics with those overrides.

    Args:
        question: User's hypothetical question.
        real_metrics: Actual metrics from evaluation_report.json.

    Returns:
        Simulated metrics dict with overridden values.
    """
    simulated = copy.deepcopy(real_metrics)
    question_lower = question.lower()

    if "metrics" not in simulated:
        simulated["metrics"] = {}

    # --- R2 simulation ---
    r2_match = re.search(r'r2\s*(?:drops?|falls?|becomes?|is|to|below|=)\s*(0\.\d+)', question_lower)
    if r2_match:
        simulated["metrics"]["r2"] = float(r2_match.group(1))
    elif "r2" in question_lower and "below 0.9" in question_lower:
        simulated["metrics"]["r2"] = 0.85
    elif "r2" in question_lower and "below 0.85" in question_lower:
        simulated["metrics"]["r2"] = 0.80
    elif "r2" in question_lower and "drops" in question_lower:
        simulated["metrics"]["r2"] = 0.85

    # --- RMSE simulation ---
    rmse_match = re.search(r'rmse\s*(?:increases?|rises?|becomes?|is|to|above|=)\s*(\d+\.?\d*)', question_lower)
    if rmse_match:
        simulated["metrics"]["rmse"] = float(rmse_match.group(1))
    elif "rmse" in question_lower and "above 20" in question_lower:
        simulated["metrics"]["rmse"] = 25.0
    elif "rmse" in question_lower and "high" in question_lower:
        simulated["metrics"]["rmse"] = 25.0

    # --- MAPE simulation ---
    mape_match = re.search(r'mape\s*(?:increases?|rises?|becomes?|is|to|above|=)\s*(\d+\.?\d*)', question_lower)
    if mape_match:
        simulated["metrics"]["mape"] = float(mape_match.group(1))
    elif "mape" in question_lower and "high" in question_lower:
        simulated["metrics"]["mape"] = 8.0

    # --- Improvement simulation ---
    imp_match = re.search(r'improvement\s*(?:drops?|falls?|becomes?|is|to|below|=)\s*(\d+\.?\d*)', question_lower)
    if imp_match:
        simulated["metrics"]["improvement_percent"] = float(imp_match.group(1))
    elif "improvement" in question_lower and "low" in question_lower:
        simulated["metrics"]["improvement_percent"] = 10.0

    return simulated


def simulate_drift(question: str, real_drift: dict) -> dict:
    """
    Override drift status based on hypothetical question.

    Args:
        question: User's hypothetical question.
        real_drift: Actual drift status.

    Returns:
        Simulated drift dict.
    """
    simulated = copy.deepcopy(real_drift)
    question_lower = question.lower()

    if "drift" in question_lower:
        if "high" in question_lower:
            simulated["drift_risk"] = "HIGH"
        elif "medium" in question_lower:
            simulated["drift_risk"] = "MEDIUM"

    return simulated
