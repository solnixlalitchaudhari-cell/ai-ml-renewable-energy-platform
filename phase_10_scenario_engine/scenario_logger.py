"""
Phase 10 — Scenario Logger

Logs all simulation runs to simulation_logs.json
with timestamps and full scenario details.

No global state. Append-only logging.
"""

import os
import json
from datetime import datetime

LOG_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(LOG_DIR, "simulation_logs.json")


def log_simulation(event: dict) -> None:
    """
    Append a simulation event to simulation_logs.json.

    Args:
        event: dict containing simulation details:
            - question: str
            - overrides: dict
            - risk_result: dict
    """
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event
    }

    # Load existing logs or start fresh
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []

    logs.append(record)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
