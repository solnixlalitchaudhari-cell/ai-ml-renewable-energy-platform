"""
Phase 13 — Tool Router (Dynamic Orchestrator)

The new brain of the system.
Replaces static rules with LLM-driven planning and execution.

Flow:
1. User Question -> LLM Planner
2. Plan -> Tool Executor
3. Results -> LLM Summarizer
"""

import json
from datetime import datetime

from phase_09_agent_orchestration.llm_client import generate_summary
from phase_09_agent_orchestration.tools import get_model_metrics
from phase_13_tool_calling.llm_planner import plan_tools
from phase_13_tool_calling.tool_executor import execute_tools

def run_dynamic_orchestration(question: str, plant_id: int = 1) -> dict:
    """
    Orchestrate the AI agent using dynamic tool selection.
    
    Args:
        question: User's query.
        plant_id: Context identifier.
        
    Returns:
        Structured response with plan, execution results, and summary.
    """
    started_at = datetime.utcnow().isoformat()
    
    # 1. Gather Context (Base Shared State)
    # This state is mutable and passed through all tools sequentially.
    shared_state = {
        "metrics": get_model_metrics(),
        "drift_status": {}, # Initial drift status
        "question": question,
        "overrides_applied": {}
    }
    
    # 2. Plan (LLM Decide)
    print(f"🤔 Planning tools for: {question}")
    plan = plan_tools(question)
    steps = plan.get("steps", [])
    
    # 3. Execute (Run Tools Sequentially)
    print(f"🛠️  Executing steps: {[s['tool'] for s in steps]}")
    tool_results = {}
    
    for step in steps:
        tool_name = step["tool"]
        tool_args = step.get("args", {})
        
        # Execute tool with CURRENT shared_state
        # Simulation engine will update the shared_state in place.
        result = execute_tools([tool_name], shared_state, args_map={tool_name: tool_args})
        tool_results.update(result)
        
        # Log when simulation updates the context implicitly
        if tool_name == "simulation_engine":
             print(f"   🔄 SharedState updated with Simulation Data (Hypothetical Mode)")

    # 4. Synthesize (LLM Summary)
    summary_prompt = (
        f"User Question: {question}\n\n"
        f"Execution Plan: {json.dumps(steps, indent=2)}\n\n"
        f"Tool Outputs:\n{json.dumps(tool_results, indent=2)}\n\n"
        f"Task: Provide a concise executive summary and final answer based on the tool outputs."
    )
    
    final_answer = generate_summary(summary_prompt)
    
    # 5. Construct Response
    return {
        "orchestration_type": "llm_dynamic_planning",
        "question": question,
        "plan": plan,
        "tool_results": tool_results,
        "final_answer": final_answer,
        "shared_state": shared_state,  # Added this to return the final mutated state!
        "metadata": {
            "started_at": started_at,
            "completed_at": datetime.utcnow().isoformat(),
            "tools_used": [s['tool'] for s in steps]
        }
    }
