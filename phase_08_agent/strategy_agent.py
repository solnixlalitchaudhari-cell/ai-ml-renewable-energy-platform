def strategy_recommendation(metrics):
    # Handle both nested and flat structure
    r2 = metrics.get("r2")
    if r2 is None:
        r2 = metrics.get("metrics", {}).get("r2", 0.0)

    if r2 < 0.95:
        return "Consider retraining model within next cycle"

    return "Continue deployment, schedule quarterly review"
