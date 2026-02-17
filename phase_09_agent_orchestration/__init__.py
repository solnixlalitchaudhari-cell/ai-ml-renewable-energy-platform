"""
Phase 9 — Intelligent Multi-Agent Orchestration Layer

Modules:
    - intent_classifier: Rule-based intent detection and agent routing
    - orchestrator: Central orchestration pipeline (run_orchestration)
    - response_aggregator: Merges agent outputs into structured JSON
    - confidence_engine: Confidence scoring based on agent agreement
    - tools: Internal tool functions (metrics, logs, drift)
"""

from phase_9_agent_orchestration.orchestrator import run_orchestration

__all__ = ["run_orchestration"]
