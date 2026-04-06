import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phase_11_alerting.severity_rules import determine_severity
from phase_09_agent_orchestration.response_aggregator import aggregate_responses

def test_severity_context():
    print("Testing determine_severity context population...")
    
    # Mock orchestration result with metrics
    result = {
        "final_decision": "CRITICAL - ACTION REQUIRED",
        "priority": "P0",
        "confidence": {"confidence_score": 0.9},
        "metrics": {
            "metrics": {
                "mape": 45.3,
                "r2": 0.82,
                "rmse": 15.5
            }
        },
        "agent_outputs": {
            "risk_assessment": {
                "risk_level": "CRITICAL",
                "estimated_financial_risk": 600000
            }
        }
    }
    
    severity = determine_severity(result)
    context = severity["context"]
    
    print(f"Severity: {severity['severity']}")
    print(f"Context: {json.dumps(context, indent=2)}")
    
    assert "forecast_deviation_percent" in context, "Missing forecast_deviation_percent"
    assert context["forecast_deviation_percent"] == 45.3, f"Wrong deviation: {context['forecast_deviation_percent']}"
    assert "anomaly_score" in context, "Missing anomaly_score"
    assert "metrics" in context, "Missing metrics"
    
    # Check if anomaly score is calculated correctly
    # (1 - 0.82) + (15.5 / 100) = 0.18 + 0.155 = 0.335 -> round to 0.34
    expected_score = 0.34
    assert context["anomaly_score"] == expected_score, f"Anomaly score {context['anomaly_score']} != {expected_score}"

    print("\u2705 determine_severity population verified.")

def test_aggregator_metrics():
    print("\nTesting aggregate_responses metrics pass-through...")
    
    agent_results = {}
    intent_info = {}
    confidence = {"confidence_score": 0.9}
    metrics_input = {"metrics": {"r2": 0.9}}
    
    response = aggregate_responses(
        agent_results, 
        intent_info, 
        confidence, 
        metrics=metrics_input
    )
    
    assert "metrics" in response, "Metrics missing from aggregated response"
    assert response["metrics"] == metrics_input, "Metrics content mismatch"
    
    print("\u2705 Aggregator passes metrics correctly.")

if __name__ == "__main__":
    try:
        test_severity_context()
        test_aggregator_metrics()
        print("\n\u2728 ALL TESTS PASSED \u2728")
    except AssertionError as e:
        print(f"\n\u274c TEST FAILED: {e}")
    except Exception as e:
        print(f"\n\u274c ERROR: {e}")
