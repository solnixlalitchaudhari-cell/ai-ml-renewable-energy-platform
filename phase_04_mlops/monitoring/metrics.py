from datetime import datetime

START_TIME = datetime.utcnow()

metrics = {
    "total_predictions": 0,
    "total_anomalies": 0,
    "last_prediction_time": None
}

def record_prediction(is_anomaly=False):
    metrics["total_predictions"] += 1
    metrics["last_prediction_time"] = datetime.utcnow()

    if is_anomaly:
        metrics["total_anomalies"] += 1

def get_metrics():
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    return {
        "uptime_seconds": uptime,
        **metrics
    }
