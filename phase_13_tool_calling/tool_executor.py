"""
Phase 13 — Tool Executor

Executes a list of selected tools safely.
Handles errors and aggregates results.
"""

from phase_13_tool_calling.tool_registry import TOOL_REGISTRY
import traceback
from pydantic import ValidationError

def execute_tools(tool_names: list, shared_state: dict, args_map: dict = None) -> dict:
    """
    Run specific tools from the registry.
    
    Args:
        tool_names: List of strings (keys in TOOL_REGISTRY).
        shared_state: Mutable shared context dict updated by tools sequentially.
        args_map: Dict mapping tool_name -> args dict.
        
    Returns:
        dict: Aggregated results from all tools.
    """
    results = {}
    if args_map is None:
        args_map = {}
    
    for name in tool_names:
        if name not in TOOL_REGISTRY:
            results[name] = {"error": f"Tool '{name}' not found in registry."}
            continue
            
        try:
            # Execute the tool function
            func = TOOL_REGISTRY[name]["func"]
            tool_args = args_map.get(name, {})
            
            # Pass args via shared_state explicitly for this tool
            shared_state["args"] = tool_args
            
            output = func(shared_state)
            
            # SCHEMA VALIDATION
            schema_model = TOOL_REGISTRY[name].get("schema")
            if schema_model:
                try:
                    # Validate output against expected Pydantic schema
                    validated = schema_model(**output)
                    output = validated.model_dump() # Convert back to dict
                except ValidationError as ve:
                    print(f"[TOOL EXECUTOR ERROR] Schema Validation Failed for {name}: {ve}")
                    output = {"error": f"Schema validation failed: {ve}"}
            
            results.update(output)
            
        except Exception as e:
            print(f"[TOOL EXECUTOR ERROR] Failed to run {name}: {e}")
            results[name] = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
    return results
