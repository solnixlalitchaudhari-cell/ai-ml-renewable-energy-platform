"""
Phase 13 — LLM Planner

Generates a tool execution plan based on user query.
Uses the LLM to select the most relevant tools.
"""

import json
from phase_09_agent_orchestration.llm_client import generate_summary
from phase_13_tool_calling.tool_registry import TOOL_REGISTRY

def plan_tools(question: str) -> dict:
    """
    Ask LLM which tools to run for the given question.
    
    Args:
        question: User's natural language query.
        
    Returns:
        dict: {
            "tools": ["tool_name_1", "tool_name_2"],
            "reasoning": "Explanation..."
        }
    """
    
    # helper to format tool descriptions
    tool_descriptions = "\n".join(
        [f"- {name}: {info['desc']}" for name, info in TOOL_REGISTRY.items()]
    )
    
    prompt = (
        f"You are an AI Agent Planner. Your job is to create a multi-step execution plan to answer the user's question.\n\n"
        f"AVAILABLE TOOLS:\n{tool_descriptions}\n\n"
        f"USER QUESTION: \"{question}\"\n\n"
        f"INSTRUCTIONS:\n"
        f"1. Break the task into local steps.\n"
        f"2. EXTRACT explicit parameter values from the question into 'args'.\n"
        f"   - Example: \"If R2 drops to 0.75\" -> args: {{ \"overrides\": {{ \"r2\": 0.75 }} }}\n"
        f"   - Example: \"financial risk exceeds 700000\" -> args: {{ \"overrides\": {{ \"estimated_financial_risk\": 700000 }} }}\n"
        f"3. Return ONLY a JSON object. No markdown, no free text.\n"
        f"4. Format:\n"
        f"{{\n"
        f"  \"steps\": [\n"
        f"    {{\n"
        f"      \"tool\": \"tool_name\",\n"
        f"      \"args\": {{ \"overrides\": {{ \"key\": value }} }},\n"
        f"      \"reason\": \"Why running this step\"\n"
        f"    }}\n"
        f"  ]\n"
        f"}}\n"
        f"5. IF hypothetical (e.g. \"what if\", \"simulate\"), YOU MUST START with 'simulation_engine'.\n"
    )
    
    response_text = generate_summary(prompt)
    
    # Attempt to parse JSON with regex fallback
    import re
    try:
        # cleanup potential markdown wrappers
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Regex to find JSON block if mixed with text
        json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
        if json_match:
            clean_text = json_match.group(0)
            
        plan = json.loads(clean_text)
        
        # Validate tools exist
        valid_steps = []
        for step in plan.get("steps", []):
            if step["tool"] in TOOL_REGISTRY:
                # Ensure args dict exists
                if "args" not in step:
                    step["args"] = {}
                valid_steps.append(step)
                
        plan["steps"] = valid_steps
        
        # Fallback if LLM hallucinations or returns empty
        if not valid_steps:
             # Default fallback plan
            plan = {
                "steps": [
                    {"tool": "ops_agent", "args": {}, "reason": "Fallback: Default operational check"},
                    {"tool": "risk_agent", "args": {}, "reason": "Fallback: Default risk check"}
                ]
            }
            
        return plan
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"[LLM PLANNER ERROR] JSON Parse Failed: {e}\nResponse: {response_text}")
        return {
            "steps": [
                {"tool": "ops_agent", "args": {}, "reason": "JSON parsing failed"},
                {"tool": "risk_agent", "args": {}, "reason": "JSON parsing failed"}
            ]
        }
