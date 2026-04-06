def ops_analysis(metrics):
    # Handle both nested and flat structure
    rmse = metrics.get("rmse")
    if rmse is None:
        rmse = metrics.get("metrics", {}).get("rmse", 0.0)
        
    r2 = metrics.get("r2")
    if r2 is None:
        r2 = metrics.get("metrics", {}).get("r2", 0.0)

    issues = []
    if rmse > 15:
        issues.append(f"High RMSE ({rmse:.2f}) indicating instability")

    if r2 < 0.9:
        issues.append(f"Low R2 ({r2:.2f}) indicating reduced accuracy")

    if not issues:
        return {
            "operational_risk": "Low",
            "reason": "Model performing within operational thresholds"
        }
    
    return {
        "operational_risk": "High" if len(issues) > 1 else "Medium",
        "reason": "; ".join(issues)
    }
