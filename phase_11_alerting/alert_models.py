"""
Phase 11 — Alert Models

Data structures for the alerting system.
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Alert:
    """Represents a single alert event."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    severity: str = "P2"
    decision: str = ""
    priority: str = "P2"
    plant_id: int = 0
    message: str = ""

    def to_dict(self) -> dict:
        """Convert Alert to a serializable dictionary."""
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "decision": self.decision,
            "priority": self.priority,
            "plant_id": self.plant_id,
            "message": self.message
        }
