"""
Phase 12 — Utility Helpers

Hash-based document IDs for duplicate prevention,
timestamp formatting, and logging setup.
"""

import hashlib
from datetime import datetime


def generate_doc_id(content: str) -> str:
    """
    Generate a deterministic document ID from content using SHA-256.
    Prevents duplicate documents in the vector store.

    Args:
        content: The text content to hash.

    Returns:
        First 16 hex chars of SHA-256 hash.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def format_timestamp(dt=None) -> str:
    """Return ISO-format timestamp string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def log_rag(message: str):
    """Print a tagged log message for Phase 12."""
    print(f"[Phase 12 RAG] {message}")
