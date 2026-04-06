"""
Phase 12 — Configuration

Centralized settings for the Vector RAG system.
"""

import os

# Base directory (project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Embedding model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# ChromaDB
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "data", "vector_store")
CHROMA_COLLECTION_NAME = "solarops_memory"

# Retrieval
DEFAULT_TOP_K = 5
SIMILARITY_THRESHOLD = 1.5  # L2 distance — lower is more similar

# Ingestion
MAX_PREDICTION_LOGS = 50  # Cap on prediction logs to ingest
