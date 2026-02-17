import os
import requests
import json
from .tools import load_evaluation_data, load_metrics_history, load_recent_logs
from .prompt_templates import build_prompt

HF_TOKEN = os.getenv("HF_TOKEN")

def run_agent(plant_id: int, question: str):

    evaluation = load_evaluation_data()
    history = load_metrics_history()
    logs = load_recent_logs()

    prompt = build_prompt(
        plant_id=plant_id,
        question=question,
        evaluation=evaluation,
        history=history,
        logs=logs
    )

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "messages": [
            {"role": "system", "content": "You are an AI Energy Operations Analyst."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 600,
        "temperature": 0.2
    }

    response = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        return {
            "error": "LLM request failed",
            "details": response.text
        }

    result = response.json()

    raw_output = result["choices"][0]["message"]["content"]

    try:
        structured = json.loads(raw_output)
        return structured
    except:
        return {
            "error": "LLM returned invalid JSON",
            "raw_output": raw_output
        }
