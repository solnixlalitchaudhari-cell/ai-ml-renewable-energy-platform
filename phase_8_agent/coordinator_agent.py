from .ops_agent import ops_analysis
from .finance_agent import finance_analysis
from .strategy_agent import strategy_recommendation

def run_multi_agent(metrics):

    ops = ops_analysis(metrics)
    finance = finance_analysis(metrics)
    strategy = strategy_recommendation(metrics)

    overall_risk = "Low"

    if ops["operational_risk"] == "High" or finance["financial_risk"] == "High":
        overall_risk = "High"

    return {
        "operational": ops,
        "financial": finance,
        "strategy": strategy,
        "overall_risk": overall_risk
    }
