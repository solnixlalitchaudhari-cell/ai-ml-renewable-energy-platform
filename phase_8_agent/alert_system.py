import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ALERT_PATH = os.path.join(BASE_DIR, "phase_8_agent", "alerts.json")

def log_alert(alert_data):
    if os.path.exists(ALERT_PATH):
        with open(ALERT_PATH, "r") as f:
            alerts = json.load(f)
    else:
        alerts = []

    alerts.append({
        "timestamp": datetime.utcnow().isoformat(),
        **alert_data
    })

    os.makedirs(os.path.dirname(ALERT_PATH), exist_ok=True)
    with open(ALERT_PATH, "w") as f:
        json.dump(alerts[-50:], f, indent=2)  # Keep last 50 alerts
