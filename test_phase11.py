"""Phase 11 — Alert System Test"""
from phase_11_alerting.alert_engine import evaluate_alert

# TEST 1: Simulated CRITICAL
print("TEST 1: Simulated R2=0.80 + drift HIGH")
r = evaluate_alert({
    "final_decision": "CRITICAL — Immediate Action Required",
    "priority": "P0",
    "confidence": {"score": 0.2, "label": "LOW", "breakdown": []},
    "agent_outputs": {
        "risk_assessment": {"risk_level": "CRITICAL", "estimated_financial_risk": 650000},
        "simulation_risk": {"risk_level": "CRITICAL", "estimated_financial_risk": 650000,
                            "risk_factors": ["R2=0.84 is below 0.85 (CRITICAL threshold)"]}
    }
}, plant_id=1)
print(f"  alert_triggered: {r['alert_triggered']}")
print(f"  severity: {r['severity']}")
print(f"  alert_type: {r['alert_type']}")
print(f"  reason: {r['reason']}")
print()

# TEST 2: Normal metrics
print("TEST 2: Normal metrics")
r2 = evaluate_alert({
    "final_decision": "STABLE — System operating normally",
    "priority": "P2",
    "confidence": {"score": 1.0, "label": "HIGH", "breakdown": []},
    "agent_outputs": {
        "risk_assessment": {"risk_level": "LOW", "estimated_financial_risk": 0}
    }
}, plant_id=1)
print(f"  alert_triggered: {r2['alert_triggered']}")
print(f"  severity: {r2['severity']}")
print(f"  alert_type: {r2['alert_type']}")
print()
print("ALL TESTS PASSED")
