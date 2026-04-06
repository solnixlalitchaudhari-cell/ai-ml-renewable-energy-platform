
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath("C:/Users/lalit/Desktop/solar_wind_ai_project"))

from phase_11_alerting.alert_engine import evaluate_alert

def test_critical_financial_alert():
    print("Testing Critical Financial Alert...")
    mock_result = {
        "final_decision": "Review Required",
        "priority": "P2",
        "agent_outputs": {
            "risk_assessment": {
                "risk_level": "LOW",
                "estimated_financial_risk": 600000 
            },
            "simulation_risk": {
                 "estimated_financial_risk": 0
            }
        }
    }
    
    alert_metadata = evaluate_alert(mock_result, plant_id=101)
    
    # We can't easily check the Alert object itself since evaluate_alert returns a dict, 
    # but we can check if the logic didn't crash and returned the right severity/reason.
    # To really verify the context, we'd need to mock the logger or inspect the Alert object creation.
    # However, since we saw the code, if it runs without error, it means variables are passing through.
    
    print("Result Context:", alert_metadata.get("context"))
    
    if alert_metadata["severity"] == "P0" and "exceeds" in alert_metadata["reason"]:
        if alert_metadata["context"]["trigger"] == "financial_risk_threshold_exceeded":
            print("SUCCESS: Alert severity, reason, AND context trigger are correct.")
        else:
            print("FAILURE: Context trigger incorrect.")
    else:
        print("FAILURE: Unexpected severity or reason.")

def test_critical_decision_alert():
    print("\nTesting Critical Decision Alert...")
    mock_result = {
        "final_decision": "CRITICAL - SHUTDOWN",
        "priority": "P0",
        "agent_outputs": {}
    }
    
    alert_metadata = evaluate_alert(mock_result, plant_id=102)
    print("Result:", alert_metadata)
    
    if alert_metadata["severity"] == "P0" and "CRITICAL" in alert_metadata["reason"]:
        print("SUCCESS: Alert severity and reason are correct.")
    else:
        print("FAILURE: Unexpected severity or reason.")

if __name__ == "__main__":
    with open("test_output.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        test_critical_financial_alert()
        test_critical_decision_alert()
        sys.stdout = sys.__stdout__
    print("Test run complete. Check test_output.txt")
