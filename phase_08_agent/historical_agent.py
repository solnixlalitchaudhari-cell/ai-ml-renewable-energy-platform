"""
Phase 8 — Historical Alert Agent (Memory Agent)

Queries historical alert data from Phase 11 alert logs
and Phase 12 vector store to answer questions about
past incidents, previous alerts, and historical patterns.

This agent is activated when the intent classifier detects
historical/memory-related questions.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Primary alert source (Phase 11 — structured logs)
ALERT_LOG_PATH = os.path.join(BASE_DIR, "phase_11_alerting", "alerts.json")

# Secondary alert source (Phase 8 — agent-level alerts)
AGENT_ALERT_PATH = os.path.join(BASE_DIR, "phase_08_agent", "alerts.json")


def _load_alerts(path: str) -> list:
    """Safely load alerts from a JSON file."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _normalize_alert(entry: dict) -> dict:
    """Normalize alert entry to a consistent format."""
    alert = entry.get("alert", entry)
    return {
        "alert_id": alert.get("alert_id", "unknown"),
        "timestamp": alert.get("timestamp", entry.get("logged_at", "")),
        "severity": alert.get("severity", "UNKNOWN"),
        "decision": alert.get("decision", ""),
        "priority": alert.get("priority", ""),
        "plant_id": alert.get("plant_id", 1),
        "message": alert.get("message", ""),
    }


def get_alert_history(
    severity_filter: str = None,
    plant_id: int = None,
    limit: int = 10,
) -> list:
    """
    Retrieve historical alerts, optionally filtered by severity and plant.

    Args:
        severity_filter: Filter by severity level (e.g. "P0", "P1").
        plant_id: Filter by plant ID.
        limit: Maximum number of alerts to return.

    Returns:
        List of normalized alert dicts, sorted newest-first.
    """
    # Merge alerts from both sources
    raw_alerts = _load_alerts(ALERT_LOG_PATH) + _load_alerts(AGENT_ALERT_PATH)

    # Normalize
    alerts = [_normalize_alert(a) for a in raw_alerts]

    # Filter by severity
    if severity_filter:
        alerts = [a for a in alerts if a["severity"] == severity_filter]

    # Filter by plant
    if plant_id is not None:
        alerts = [a for a in alerts if a["plant_id"] == plant_id]

    # Sort newest first
    alerts.sort(key=lambda a: a["timestamp"], reverse=True)

    return alerts[:limit]


def get_last_critical_alert(plant_id: int = None) -> dict | None:
    """Get the most recent P0 CRITICAL alert."""
    alerts = get_alert_history(severity_filter="P0", plant_id=plant_id, limit=1)
    return alerts[0] if alerts else None


def historical_analysis(question: str, plant_id: int = 1) -> dict:
    """
    Main entry point for the historical/memory agent.
    Analyzes the question to determine what historical data to retrieve,
    then returns structured results.

    Args:
        question: The user's natural language question.
        plant_id: The plant to query history for.

    Returns:
        Structured dict with historical findings.
    """
    question_lower = question.lower()

    # Determine what to look for
    severity_filter = None
    if any(k in question_lower for k in ["critical", "p0", "urgent", "emergency"]):
        severity_filter = "P0"
    elif any(k in question_lower for k in ["warning", "p1"]):
        severity_filter = "P1"

    # Determine how many to retrieve
    limit = 1 if any(k in question_lower for k in ["last", "most recent", "latest"]) else 10

    # Retrieve alerts
    alerts = get_alert_history(
        severity_filter=severity_filter,
        plant_id=plant_id,
        limit=limit,
    )

    # Also query Phase 12 Vector RAG for semantic context
    rag_context = ""
    try:
        from phase_12_vector_rag.rag_engine import run_rag
        rag_result = run_rag(question, plant_id=plant_id)
        rag_context = rag_result.get("context", "")
    except Exception:
        pass

    # Build summary
    total_alerts = len(_load_alerts(ALERT_LOG_PATH) + _load_alerts(AGENT_ALERT_PATH))
    critical_count = len(get_alert_history(severity_filter="P0"))
    warning_count = len(get_alert_history(severity_filter="P1"))

    if alerts:
        last = alerts[0]
        executive_summary = (
            f"Found {len(alerts)} matching alert(s). "
            f"Most recent: {last['severity']} alert on {last['timestamp']} — "
            f"{last['message']}"
        )
    else:
        executive_summary = "No matching historical alerts found."

    return {
        "historical_analysis": {
            "executive_summary": executive_summary,
            "matching_alerts": alerts,
            "alert_statistics": {
                "total_alerts": total_alerts,
                "critical_p0": critical_count,
                "warning_p1": warning_count,
            },
            "rag_context": rag_context,
        }
    }
