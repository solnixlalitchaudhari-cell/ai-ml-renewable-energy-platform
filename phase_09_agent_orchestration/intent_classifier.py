"""
Phase 9 — Intent Classifier Module

Rule-based intent detection that analyzes user questions
and determines which agents should be activated.
"""

# Agent routing keywords
INTENT_MAP = {
    "risk_agent": ["drift", "risk", "anomaly", "degradation", "unstable"],
    "finance_agent": ["financial", "revenue", "loss", "cost", "money", "roi", "budget"],
    "executive_agent": ["summary", "executive", "overview", "report", "status", "dashboard"],
    "ops_agent": ["operational", "performance", "rmse", "accuracy", "model", "metric", "r2"],
}


def classify_intent(question: str) -> dict:
    """
    Analyze user question and determine which agents to activate.

    Args:
        question: The user's natural language question.

    Returns:
        dict with:
            - selected_agents: list of agent names to activate
            - detected_intents: list of matched keywords
            - routing_type: 'targeted' if specific match, 'broadcast' if all
    """
    question_lower = question.lower()
    selected_agents = set()
    detected_intents = []

    # Detect hypothetical / what-if intent
    from phase_9_agent_orchestration.scenario_engine import is_hypothetical
    hypothetical = is_hypothetical(question)

    for agent_name, keywords in INTENT_MAP.items():
        for keyword in keywords:
            if keyword in question_lower:
                selected_agents.add(agent_name)
                detected_intents.append({
                    "keyword": keyword,
                    "routed_to": agent_name
                })

    # If hypothetical, always broadcast to all agents
    if hypothetical:
        selected_agents = set(INTENT_MAP.keys())
        routing_type = "simulation"
    elif not selected_agents:
        selected_agents = set(INTENT_MAP.keys())
        routing_type = "broadcast"
    else:
        routing_type = "targeted"

    return {
        "selected_agents": sorted(list(selected_agents)),
        "detected_intents": detected_intents,
        "routing_type": routing_type,
        "is_hypothetical": hypothetical,
        "agent_count": len(selected_agents)
    }
