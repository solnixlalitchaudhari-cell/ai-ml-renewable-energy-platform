"""
Phase 12 — ChromaDB Vector Store

Persistent vector database using ChromaDB.
Collection: solarops_memory
Persists to: data/vector_store/
"""

import os
import chromadb
from phase_12_vector_rag.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from phase_12_vector_rag.utils import log_rag

# Ensure persist directory exists
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

# Initialize persistent ChromaDB client
_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

# Get or create collection
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION_NAME,
    metadata={"hnsw:space": "l2"}
)


def get_collection():
    """Return the raw ChromaDB collection for advanced use."""
    return _collection


def add_documents(ids: list, documents: list, embeddings: list, metadatas: list):
    """
    Add documents to the vector store with duplicate prevention.

    Skips any document whose ID already exists in the collection.

    Args:
        ids: List of unique document IDs (hash-based).
        documents: List of text content strings.
        embeddings: List of embedding vectors.
        metadatas: List of metadata dicts.
    """
    if not ids:
        return 0

    # Filter out duplicates
    existing = set()
    try:
        result = _collection.get(ids=ids)
        if result and result["ids"]:
            existing = set(result["ids"])
    except Exception:
        pass

    new_ids = []
    new_docs = []
    new_embs = []
    new_metas = []

    for i, doc_id in enumerate(ids):
        if doc_id not in existing:
            new_ids.append(doc_id)
            new_docs.append(documents[i])
            new_embs.append(embeddings[i])
            new_metas.append(metadatas[i])

    if not new_ids:
        return 0

    _collection.add(
        ids=new_ids,
        documents=new_docs,
        embeddings=new_embs,
        metadatas=new_metas,
    )
    return len(new_ids)


def query(query_embedding: list, top_k: int = 5, filters: dict = None) -> dict:
    """
    Search the vector store for similar documents.

    Args:
        query_embedding: Embedding vector of the query.
        top_k: Number of results to return.
        filters: Optional ChromaDB where-filter dict
                 e.g. {"plant_id": "1"} or {"doc_type": "AlertRecord"}

    Returns:
        ChromaDB query result dict with ids, documents,
        metadatas, and distances.
    """
    if _collection.count() == 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": min(top_k, _collection.count()),
    }
    if filters:
        kwargs["where"] = filters

    try:
        return _collection.query(**kwargs)
    except Exception as e:
        log_rag(f"Query error: {e}")
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}


def get_stats() -> dict:
    """
    Return vector store statistics.

    Returns:
        Dict with total count, per-type breakdown,
        last ingestion timestamp, and health status.
    """
    total = _collection.count()

    type_counts = {}
    if total > 0:
        try:
            all_docs = _collection.get(include=["metadatas"])
            for meta in all_docs.get("metadatas", []):
                doc_type = meta.get("doc_type", "unknown")
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

            timestamps = [
                meta.get("timestamp", "") for meta in all_docs.get("metadatas", [])
            ]
            timestamps = [t for t in timestamps if t]
            last_ingestion = max(timestamps) if timestamps else None
        except Exception:
            last_ingestion = None
    else:
        last_ingestion = None

    return {
        "total_documents": total,
        "documents_per_type": type_counts,
        "last_ingestion_timestamp": last_ingestion,
        "health": "healthy" if total > 0 else "empty",
        "persist_directory": CHROMA_PERSIST_DIR,
    }
