"""
Phase 12 — Retriever

Semantic search over the ChromaDB vector store with
plant_id metadata filtering and similarity threshold.
"""

from phase_12_vector_rag.embedding_model import encode_text
from phase_12_vector_rag.vector_store import query
from phase_12_vector_rag.config import DEFAULT_TOP_K, SIMILARITY_THRESHOLD
from phase_12_vector_rag.utils import log_rag


def retrieve_relevant_documents(
    question: str,
    plant_id: int = None,
    top_k: int = DEFAULT_TOP_K,
    doc_type: str = None,
) -> list:
    """
    Retrieve the most relevant historical documents for a question.

    Args:
        question: User's natural language query.
        plant_id: Optional plant filter.
        top_k: Max results to return.
        doc_type: Optional filter by document type
                  (AlertRecord, SimulationResult, etc.)

    Returns:
        List of dicts, each with:
          - content: document text
          - metadata: metadata dict
          - distance: L2 distance (lower = more similar)
          - relevance_score: normalised 0→1 score
    """
    # Embed the question
    query_embedding = encode_text(question)

    # Build metadata filter
    filters = {}
    if plant_id is not None and doc_type:
        filters = {
            "$and": [
                {"plant_id": str(plant_id)},
                {"doc_type": doc_type},
            ]
        }
    elif plant_id is not None:
        filters = {"plant_id": str(plant_id)}
    elif doc_type:
        filters = {"doc_type": doc_type}

    result = query(query_embedding, top_k=top_k, filters=filters if filters else None)

    # Parse and rank results
    documents = []
    ids = result.get("ids", [[]])[0]
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]

    for i, doc_id in enumerate(ids):
        distance = dists[i] if i < len(dists) else 999
        # Skip results beyond similarity threshold
        if distance > SIMILARITY_THRESHOLD:
            continue

        relevance = max(0.0, 1.0 - (distance / SIMILARITY_THRESHOLD))

        documents.append({
            "id": doc_id,
            "content": docs[i] if i < len(docs) else "",
            "metadata": metas[i] if i < len(metas) else {},
            "distance": round(distance, 4),
            "relevance_score": round(relevance, 4),
        })

    return documents
