"""
Phase 10 — Metric Override Engine

Takes real evaluation metrics and applies simulation overrides
to produce a modified metrics dictionary.

No global state. No side effects. Pure functional logic.
"""


def apply_metric_overrides(metrics: dict, overrides: dict) -> dict:
    """
    Apply simulation overrides to real metrics.

    Args:
        metrics: Real evaluation metrics dict (from evaluation_report.json).
        overrides: Override dict from scenario_detector.detect_scenario().
            Keys: r2, drift_risk, mae, accuracy_drop_pct — any can be None.

    Returns:
        Modified metrics dict with overrides applied.
    """
    modified = metrics.copy()

    # Ensure nested metrics dict exists
    if "metrics" in modified:
        modified["metrics"] = modified["metrics"].copy()
    else:
        modified["metrics"] = {}

    # --- Apply R2 override ---
    if overrides.get("r2") is not None:
        modified["r2"] = overrides["r2"]
        modified["metrics"]["r2"] = overrides["r2"]

    # --- Apply drift override ---
    if overrides.get("drift_risk") is not None:
        modified["drift_risk"] = overrides["drift_risk"]

    # --- Apply MAE override ---
    if overrides.get("mae") is not None:
        modified["mae"] = overrides["mae"]
        modified["metrics"]["mae"] = overrides["mae"]

    # --- Apply accuracy drop ---
    if overrides.get("accuracy_drop_pct") is not None:
        current_r2 = modified.get("r2", modified["metrics"].get("r2", 0.99))
        drop_factor = 1 - (overrides["accuracy_drop_pct"] / 100)
        new_r2 = round(current_r2 * drop_factor, 4)
        modified["r2"] = new_r2
        modified["metrics"]["r2"] = new_r2

    return modified
