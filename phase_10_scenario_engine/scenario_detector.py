"""
Phase 10 — Scenario Detector

Detects hypothetical "what-if" simulation questions and
extracts specific metric overrides from user text.

Supported overrides:
    - R2 drops below/to X
    - Drift becomes HIGH/MEDIUM/LOW
    - MAE increases to X
    - Accuracy drops X%
"""

import re
from typing import Optional


def detect_scenario(question: str) -> dict:
    """
    Detect if user is asking a simulation question and
    extract metric overrides from the text.

    Args:
        question: User's natural language question.

    Returns:
        {
            "is_simulation": bool,
            "overrides": {
                "r2": float or None,
                "drift_risk": str or None,
                "mae": float or None,
                "accuracy_drop_pct": float or None
            }
        }
    """
    q = question.lower()
    overrides: dict = {
        "r2": None,
        "drift_risk": None,
        "mae": None,
        "accuracy_drop_pct": None
    }

    is_simulation = False

    # --- Trigger word detection ---
    trigger_words = [
        "what if", "simulate", "assume", "suppose",
        "imagine", "what happens", "scenario",
        "drops below", "drops to", "falls to",
        "increases to", "rises to", "becomes"
    ]

    if any(word in q for word in trigger_words):
        is_simulation = True

    # --- R2 override ---
    r2_match = re.search(
        r"r2\s+(?:drops?\s+(below|to)\s+|falls?\s+(below|to)\s+|becomes?\s+|is\s+|=\s*)(0\.\d+)",
        q
    )
    if r2_match:
        r2_val = float(r2_match.group(3))
        # "below X" means simulate slightly under the threshold
        if r2_match.group(1) == "below" or r2_match.group(2) == "below":
            r2_val = round(r2_val - 0.01, 4)
        overrides["r2"] = r2_val
        is_simulation = True

    # --- Drift override ---
    if "drift" in q:
        if "high" in q:
            overrides["drift_risk"] = "HIGH"
            is_simulation = True
        elif "medium" in q:
            overrides["drift_risk"] = "MEDIUM"
            is_simulation = True
        elif "low" in q:
            overrides["drift_risk"] = "LOW"
            is_simulation = True

    # --- MAE override ---
    mae_match = re.search(
        r"mae\s+(?:increases?\s+(?:to\s+)?|rises?\s+(?:to\s+)?|becomes?\s+|is\s+|=\s*|above\s+)(\d+\.?\d*)",
        q
    )
    if mae_match:
        overrides["mae"] = float(mae_match.group(1))
        is_simulation = True

    # --- Accuracy drop override ---
    acc_match = re.search(
        r"accuracy\s*(?:drops?|falls?|decreases?)\s*(\d+\.?\d*)\s*%?",
        q
    )
    if acc_match:
        overrides["accuracy_drop_pct"] = float(acc_match.group(1))
        is_simulation = True

    return {
        "is_simulation": is_simulation,
        "overrides": overrides
    }
