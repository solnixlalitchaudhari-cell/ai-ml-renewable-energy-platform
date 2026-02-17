import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

STATS_PATH = os.path.join(
    BASE_DIR,
    "phase_4_mlops",
    "drift",
    "training_stats.json"
)

with open(STATS_PATH, "r") as f:
    TRAINING_STATS = json.load(f)


def check_drift(feature_name, value, threshold=3):
    """
    Z-score based drift detection
    """
    mean = TRAINING_STATS[feature_name]["mean"]
    std = TRAINING_STATS[feature_name]["std"]

    if std == 0:
        return False

    z_score = abs(value - mean) / std

    return z_score > threshold
