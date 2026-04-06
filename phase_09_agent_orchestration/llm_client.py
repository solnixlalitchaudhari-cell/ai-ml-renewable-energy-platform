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
        # Try Docker-internal host first
        url = "http://host.docker.internal:11434/api/generate"
        try:
            response = requests.post(
                url,
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
        except requests.exceptions.RequestException:
            # Fallback to localhost for local testing
            url = "http://localhost:11434/api/generate"
            response = requests.post(
                url,
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )

        data = response.json()
        return data.get("response", "LLM returned empty response")

    except Exception as e:
        return f"LLM call failed: {str(e)}"
