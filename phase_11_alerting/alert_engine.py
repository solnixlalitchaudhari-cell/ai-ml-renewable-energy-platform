"""
Phase 11 — Alert Engine

Main entry point for the alerting system.
Evaluates orchestration output, determines severity,
triggers appropriate alerts, and logs events.
"""

from datetime import datetime

from phase_11_alerting.severity_rules import determine_severity
from phase_11_alerting.alert_logger import log_alert
from phase_11_alerting.alert_models import Alert


def evaluate_alert(orchestration_result: dict, plant_id: int) -> dict:
    """
    Evaluate orchestration result and trigger alerts if needed.

    Args:
        orchestration_result: Full response from run_orchestration().
        plant_id: Solar plant identifier.

    Returns:
        Alert metadata dict with trigger status and details.
    """

    # Step 1 — Determine severity
    severity_info = determine_severity(orchestration_result)
    severity = severity_info["severity"]
    reason = severity_info["reason"]

    # Step 2 — Build alert object
    alert = Alert(
        severity=severity,
        decision=orchestration_result.get("final_decision", ""),
        priority=orchestration_result.get("priority", "P2"),
        plant_id=plant_id,
        message=reason
    )

    # Step 3 — Trigger based on severity
    alert_triggered = False
    alert_type = "NONE"

    if severity == "P0":
        trigger_critical_alert(alert)
        alert_triggered = True
        alert_type = "CRITICAL_ALERT"

    elif severity == "P1":
        trigger_warning_alert(alert)
        alert_triggered = True
        alert_type = "WARNING_ALERT"

    # Step 4 — Return metadata
    return {
        "alert_triggered": alert_triggered,
        "severity": severity,
        "alert_type": alert_type,
        "reason": reason,
        "alert_id": alert.alert_id,
        "timestamp": alert.timestamp
    }


def trigger_critical_alert(alert: Alert) -> None:
    """
    Handle P0 CRITICAL alert.
    Logs to file and prints structured console message.
    """
    print("=" * 60)
    print(f"🚨 CRITICAL ALERT [P0] — Plant {alert.plant_id}")
    print(f"   Alert ID:  {alert.alert_id}")
    print(f"   Decision:  {alert.decision}")
    print(f"   Reason:    {alert.message}")
    print(f"   Timestamp: {alert.timestamp}")
    print("=" * 60)

    log_alert(alert.to_dict())


def trigger_warning_alert(alert: Alert) -> None:
    """
    Handle P1 WARNING alert.
    Logs to file and prints structured console message.
    """
    print("-" * 60)
    print(f"⚠️  WARNING ALERT [P1] — Plant {alert.plant_id}")
    print(f"   Alert ID:  {alert.alert_id}")
    print(f"   Decision:  {alert.decision}")
    print(f"   Reason:    {alert.message}")
    print(f"   Timestamp: {alert.timestamp}")
    print("-" * 60)

    log_alert(alert.to_dict())
