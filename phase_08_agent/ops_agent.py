def ops_analysis(metrics):
    rmse = metrics["metrics"]["rmse"]
    r2 = metrics["metrics"]["r2"]

    if rmse > 20:
        return {
            "operational_risk": "High",
            "reason": "High RMSE indicates unstable predictions"
        }

    if r2 < 0.9:
        return {
            "operational_risk": "Medium",
            "reason": "Low R2 indicates reduced accuracy"
        }

    return {
        "operational_risk": "Low",
        "reason": "Model performing within operational thresholds"
    }
