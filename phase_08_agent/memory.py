import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MEMORY_PATH = os.path.join(BASE_DIR, "phase_8_agent", "ai_memory.json")

def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r") as f:
            return json.load(f)
    return []

def save_memory(memory):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "w") as f:
        json.dump(memory[-10:], f, indent=2)  # Keep last 10 conversations

def add_memory(entry):
    memory = load_memory()
    memory.append(entry)
    save_memory(memory)
