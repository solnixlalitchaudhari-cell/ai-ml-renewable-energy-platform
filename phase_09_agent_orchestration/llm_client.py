"""
Phase 9 — LLM Client (Infrastructure Adapter)

Uses Ollama local LLM for reliable, token-free inference.
No external API keys or quotas required.
"""

import requests


def generate_summary(prompt: str) -> str:
    """
    Send a prompt to Ollama local LLM and return the generated text.

    Args:
        prompt: The user-facing prompt string.

    Returns:
        LLM-generated response string.
    """
    try:
        response = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        data = response.json()
        return data.get("response", "LLM returned empty response")

    except Exception as e:
        return f"LLM call failed: {str(e)}"
