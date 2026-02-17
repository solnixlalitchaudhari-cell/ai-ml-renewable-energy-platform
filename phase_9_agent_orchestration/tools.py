import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def get_model_metrics():
    path = os.path.join(BASE_DIR, "phase_6_evaluation", "evaluation_report.json")
    if not os.path.exists(path):
        return {"error": "Metrics not found"}
    with open(path, "r") as f:
        return json.load(f)


def get_recent_logs(limit=5):
    path = os.path.join(BASE_DIR, "phase_4_mlops", "logging", "prediction_logs.json")
    if not os.path.exists(path):
        return {"error": "Logs not found"}
    with open(path, "r") as f:
        logs = json.load(f)
    return logs[-limit:]


def get_drift_status():
    metrics = get_model_metrics()
    if "metrics" not in metrics:
        return {"error": "No metrics available"}

    improvement = metrics["metrics"].get("improvement_percent", 0)
    r2 = metrics["metrics"].get("r2", 0)

    if r2 < 0.95 or improvement < 10:
        return {"drift_risk": "HIGH"}
    return {"drift_risk": "LOW"}
