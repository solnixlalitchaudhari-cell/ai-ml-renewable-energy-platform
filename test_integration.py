import sys
import os
import json
import requests

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phase_09_agent_orchestration.orchestrator import run_orchestration

def test_full_pipeline():
    # Test 1: Hypothetical (Should use Phase 13 Planner)
    print("\n\n🧪 Test 1: Hypothetical Query (Phase 13 Planner)")
    q1 = "What is the financial impact if drift increases?"
    result1 = run_orchestration(101, q1)
    
    print(f"Orchestration Type: {result1.get('orchestration_type')}")
    print(f"Agents Used: {result1.get('orchestration_metadata', {}).get('selected_agents')}")
    
    if result1.get("orchestration_type") == "llm_dynamic_planning":
        print("✅ SUCCESS: Switched to Dynamic Planning")
        tools = result1.get('orchestration_metadata', {}).get('selected_agents', [])
        if "simulation_engine" in tools and "finance_agent" in tools:
             print("✅ SUCCESS: Correct tool chain (Sim -> Finance)")
        else:
             print(f"❌ FAILURE: Incorrect tool chain: {tools}")
    else:
        print(f"❌ FAILURE: Still using {result1.get('orchestration_type')}")


    # Test 2: Knowledge Lookup (Should stay in Phase 9 fast path)
    print("\n\n🧪 Test 2: Historical/Memory Query (Phase 9 Fast Path)")
    q2 = "What was the last critical alert?"
    result2 = run_orchestration(101, q2)
    
    routing = result2.get("routing", {}) # Phase 9 structure differs slightly, might be in root or metadata
    # Check checks
    orch_meta = result2.get("orchestration_metadata", {})
    
    print(f"Orchestration Type: {orch_meta.get('routing_type')}")
    
    if orch_meta.get("routing_type") == "knowledge_lookup":
        print("✅ SUCCESS: Stayed in Knowledge Lookup fast path")
    else:
        print(f"❌ FAILURE: Incorrect routing: {orch_meta.get('routing_type')}")

if __name__ == "__main__":
    test_full_pipeline()
