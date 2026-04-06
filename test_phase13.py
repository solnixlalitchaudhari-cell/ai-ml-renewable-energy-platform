import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phase_13_tool_calling.tool_router import run_dynamic_orchestration

def test_dynamic_routing():
    queries = [
        "What is the financial risk if drift increases?",
        "Is the model performance stable?",
        "Simulate a critical failure in the system."
    ]
    
    for q in queries:
        print(f"\n\n❓ Testing Query: \"{q}\"")
        try:
            result = run_dynamic_orchestration(q)
            
            print(f"✅ Plan: {json.dumps(result['plan'], indent=2)}")
            print(f"🛠️  Tools Used: {result['metadata']['tools_used']}")
            print(f"📝 Final Answer: {result['final_answer'][:100]}...")
            
            # Basic validation
            if "financial" in q.lower() and "if" in q.lower():
                 tools = result['metadata']['tools_used']
                 assert "simulation_engine" in tools, "Hypothetical query missing simulation_engine"
                 assert "finance_agent" in tools, "Financial query missing finance_agent"
                 # Check order
                 sim_idx = tools.index("simulation_engine")
                 fin_idx = tools.index("finance_agent")
                 assert sim_idx < fin_idx, "Simulation must run BEFORE finance analysis"
                 print("✅ Validated: Simulation -> Finance chain")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_dynamic_routing()
