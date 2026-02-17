"""
Phase 10 — Enterprise Scenario Simulation Engine

Production-ready simulation engine for hypothetical reasoning:
    detect_scenario         — Detect what-if questions, extract overrides
    apply_metric_overrides  — Override real metrics with simulated values
    recalculate_risk        — Recalculate risk/priority from modified metrics
    log_simulation          — Log simulation events to simulation_logs.json
"""

from phase_10_scenario_engine.scenario_detector import detect_scenario
from phase_10_scenario_engine.metric_override_engine import apply_metric_overrides
from phase_10_scenario_engine.risk_recalculator import recalculate_risk
from phase_10_scenario_engine.scenario_logger import log_simulation
