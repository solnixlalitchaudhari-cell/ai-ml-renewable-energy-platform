"""
Phase 12 — Production Vector RAG System

Persistent ChromaDB vector store with semantic retrieval
for contextual LLM augmentation.
"""

from phase_12_vector_rag.ingestion_pipeline import run_full_ingestion, ingest_single_document
from phase_12_vector_rag.rag_engine import run_rag, ask_with_rag
from phase_12_vector_rag.retriever import retrieve_relevant_documents
from phase_12_vector_rag.vector_store import get_stats

__all__ = [
    "run_full_ingestion",
    "ingest_single_document",
    "run_rag",
    "ask_with_rag",
    "retrieve_relevant_documents",
    "get_stats",
]
