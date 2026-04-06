import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phase_13_tool_calling.tool_router import run_dynamic_orchestration

def test_level3_planning():
    print("\n\n🧪 Test Level 3: Parameterized Planning")
    q = "If R2 drops to 0.75, what is the risk?"
    
    try:
        result = run_dynamic_orchestration(q)
        
        steps = result['plan'].get('steps', [])
        print(f"✅ Plan Steps: {json.dumps(steps, indent=2)}")
        
        sim_step = next((s for s in steps if s['tool'] == 'simulation_engine'), None)
        
        if sim_step:
            args = sim_step.get('args', {})
            overrides = args.get('overrides', {})
            r2_val = overrides.get('r2')
            
            print(f"🔍 Extracted R2: {r2_val}")
            
            if r2_val == 0.75:
                print("✅ SUCCESS: Correctly extracted parameter R2=0.75")
            else:
                 print(f"❌ FAILURE: Expected R2=0.75, got {r2_val}")
        else:
            print("❌ FAILURE: No simulation_engine in plan")
            
        # Check execution results
        sim_result = result.get('tool_results', {}).get('simulation_result', {})
        sim_metrics = sim_result.get('metrics', {}).get('metrics', {})
        executed_r2 = sim_metrics.get('r2')
        print(f"🛠️  Executed Simulation R2: {executed_r2}")
        
        if executed_r2 == 0.75:
             print("✅ SUCCESS: Simulation Engine used the override value.")
        else:
             print(f"❌ FAILURE: Simulation Engine ignored override. Used {executed_r2}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_level3_planning()
