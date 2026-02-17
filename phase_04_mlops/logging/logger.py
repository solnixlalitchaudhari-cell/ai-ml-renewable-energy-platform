import csv
import os
from datetime import datetime

LOG_DIR = "phase_4_mlops/logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "predictions_log.csv")

HEADERS = [
    "timestamp",
    "endpoint",
    "dc_power",
    "ac_power",
    "prediction",
    "status",
    "model_version"
]

def log_prediction(
    endpoint,
    dc_power,
    ac_power,
    prediction,
    status,
    model_version
):
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(HEADERS)

        writer.writerow([
            datetime.utcnow().isoformat(),
            endpoint,
            dc_power,
            ac_power,
            prediction,
            status,
            model_version
        ])
