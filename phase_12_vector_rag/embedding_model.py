"""
Phase 12 — Embedding Model

Wraps sentence-transformers to produce 384-dim embeddings.
Model is loaded lazily on first call.
"""

from sentence_transformers import SentenceTransformer
from phase_12_vector_rag.config import EMBEDDING_MODEL_NAME
from phase_12_vector_rag.utils import log_rag

_model = None


def _get_model():
    """Lazy-load the SentenceTransformer model."""
    global _model
    if _model is None:
        log_rag(f"Loading embedding model: {EMBEDDING_MODEL_NAME} ...")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        log_rag("Embedding model loaded.")
    return _model


def encode_text(text: str) -> list:
    """
    Encode a single text string into an embedding vector.

    Args:
        text: Any string.

    Returns:
        List of floats (384-dim).
    """
    model = _get_model()
    return model.encode(text).tolist()


def encode_batch(texts: list) -> list:
    """
    Encode a batch of text strings into embedding vectors.

    Args:
        texts: List of strings.

    Returns:
        List of lists of floats.
    """
    if not texts:
        return []
    model = _get_model()
    return model.encode(texts).tolist()
