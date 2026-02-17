import requests
import os
import json

from .tools import get_model_metrics, get_drift_status, get_recent_logs

HF_TOKEN = os.getenv("HF_TOKEN")

TOOLS = {
    "get_model_metrics": get_model_metrics,
    "get_drift_status": get_drift_status,
    "get_recent_logs": get_recent_logs
}


def select_tool(question):
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "messages": [
            {
                "role": "system",
                "content": """
You are an AI Agent Router.

Available tools:
1. get_model_metrics – use for model performance questions
2. get_drift_status – use for drift related questions
3. get_recent_logs – use for operational or anomaly questions

Return ONLY JSON:
{"tool_name": "tool_name_here"}
"""
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 100,
        "temperature": 0
    }

    response = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers=headers,
        json=payload
    )

    result = response.json()
    raw = result["choices"][0]["message"]["content"]
    raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)["tool_name"]


def run_agent(question):
    tool_name = select_tool(question)

    if tool_name not in TOOLS:
        return {"error": "Invalid tool selected"}

    tool_result = TOOLS[tool_name]()

    return {
        "selected_tool": tool_name,
        "tool_result": tool_result
    }
