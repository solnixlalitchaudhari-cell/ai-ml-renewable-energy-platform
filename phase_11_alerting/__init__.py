"""
Phase 11 — Alerting & Escalation System

Production-grade alerting for AI-powered renewable energy platform.

    evaluate_alert      — Main entry: evaluate orchestration result and trigger alerts
    determine_severity  — Determine P0/P1/P2 severity from results
    log_alert           — Append alert record to alerts.json
    Alert               — Alert data model
"""

from phase_11_alerting.alert_engine import evaluate_alert
from phase_11_alerting.severity_rules import determine_severity
from phase_11_alerting.alert_logger import log_alert
from phase_11_alerting.alert_models import Alert
