def strategy_recommendation(metrics):
    r2 = metrics["metrics"]["r2"]

    if r2 < 0.95:
        return "Consider retraining model within next cycle"

    return "Continue deployment, schedule quarterly review"
