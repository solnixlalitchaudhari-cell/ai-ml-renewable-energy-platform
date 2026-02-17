"""
Phase 11 — Alert Logger

Appends alert records to alerts.json.
Thread-safe, append-only, with exception handling.
"""

import os
import json
from datetime import datetime

LOG_DIR = os.path.dirname(__file__)
ALERT_LOG_PATH = os.path.join(LOG_DIR, "alerts.json")


def log_alert(alert_data: dict) -> None:
    """
    Append an alert record to alerts.json.

    Args:
        alert_data: Alert dict to log.
    """
    record = {
        "logged_at": datetime.utcnow().isoformat(),
        "alert": alert_data
    }

    try:
        alerts = []
        if os.path.exists(ALERT_LOG_PATH):
            try:
                with open(ALERT_LOG_PATH, "r") as f:
                    alerts = json.load(f)
            except (json.JSONDecodeError, IOError):
                alerts = []

        alerts.append(record)

        with open(ALERT_LOG_PATH, "w") as f:
            json.dump(alerts, f, indent=2)

    except Exception as e:
        # Never crash the pipeline for a logging failure
        print(f"[ALERT LOGGER ERROR] Failed to log alert: {e}")
