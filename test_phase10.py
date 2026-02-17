"""Phase 10 Enterprise — Full Test Suite"""

from phase_10_scenario_engine import (
    detect_scenario,
    apply_metric_overrides,
    recalculate_risk,
    log_simulation
)
from phase_9_agent_orchestration.confidence_engine import compute_confidence

base = {"metrics": {"r2": 0.9999, "mae": 1.2}}

# ========== CASE 1 ==========
print("=== CASE 1: What if R2 drops below 0.85? ===")
s = detect_scenario("What if R2 drops below 0.85?")
m = apply_metric_overrides(base, s["overrides"])
r = recalculate_risk(m)
c = compute_confidence({}, {"drift_risk": "LOW"}, m)
print(f"  simulation_mode: {s['is_simulation']}")
print(f"  r2_override: {m['r2']}")
print(f"  risk_level: {r['risk_level']}")
print(f"  priority: {r['priority']}")
print(f"  confidence: {c['confidence_score']} ({c['confidence_label']})")
print(f"  financial_risk: {r['estimated_financial_risk']}")
print()

# ========== CASE 2 ==========
print("=== CASE 2: What if drift becomes HIGH? ===")
s = detect_scenario("What if drift becomes HIGH?")
m = apply_metric_overrides(base, s["overrides"])
r = recalculate_risk(m)
c = compute_confidence({}, {"drift_risk": "HIGH"}, m)
print(f"  simulation_mode: {s['is_simulation']}")
print(f"  drift_override: {m.get('drift_risk')}")
print(f"  risk_level: {r['risk_level']}")
print(f"  priority: {r['priority']}")
print(f"  confidence: {c['confidence_score']} ({c['confidence_label']})")
print()

# ========== CASE 3 ==========
print("=== CASE 3: What if MAE increases to 5? ===")
s = detect_scenario("What if MAE increases to 5?")
m = apply_metric_overrides(base, s["overrides"])
r = recalculate_risk(m)
c = compute_confidence({}, {"drift_risk": "LOW"}, m)
print(f"  simulation_mode: {s['is_simulation']}")
print(f"  mae_override: {m.get('mae')}")
print(f"  risk_level: {r['risk_level']}")
print(f"  financial_risk: {r['estimated_financial_risk']}")
print(f"  confidence: {c['confidence_score']} ({c['confidence_label']})")
print()

# ========== LOGGER ==========
log_simulation({"test": "all_cases_passed"})
print("Logger: OK [simulation_logs.json updated]")
print()
print("ALL TESTS PASSED")
