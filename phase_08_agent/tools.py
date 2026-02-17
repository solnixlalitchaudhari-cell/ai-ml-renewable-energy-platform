import json
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)


def get_model_metrics():
    path = os.path.join(BASE_DIR, "phase_6_evaluation", "evaluation_report.json")
    if not os.path.exists(path):
        return {"error": "metrics not found"}
    with open(path) as f:
        return json.load(f)


def get_drift_status():
    path = os.path.join(BASE_DIR, "phase_4_mlops", "drift", "training_stats.json")
    if not os.path.exists(path):
        return {"error": "drift stats not found"}
    with open(path) as f:
        return json.load(f)


def get_recent_logs():
    path = os.path.join(BASE_DIR, "phase_4_mlops", "logging", "prediction_logs.json")
    if not os.path.exists(path):
        return {"error": "logs not found"}
    with open(path) as f:
        return json.load(f)[-5:]


def load_evaluation_data():
    return get_model_metrics()


def load_metrics_history():
    path = os.path.join(BASE_DIR, "phase_6_evaluation", "metrics_history.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)[-3:]
    return []


def load_recent_logs():
    return get_recent_logs()
