"""
Phase 12 — RAG Engine

Main entry point for retrieval-augmented generation.
Retrieves relevant documents, builds a context block,
formats a structured prompt, computes a confidence boost,
and optionally generates a grounded answer via Ollama.
"""

import requests
from phase_12_vector_rag.retriever import retrieve_relevant_documents
from phase_12_vector_rag.utils import log_rag

# Ollama configuration
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
OLLAMA_MODEL = "mistral"
OLLAMA_TIMEOUT = 60


def run_rag(question: str, plant_id: int = None, top_k: int = 5) -> dict:
    """
    RAG retrieval pipeline: retrieve -> build context -> score.
    Used by the orchestrator for context injection.

    Args:
        question: User's natural language question.
        plant_id: Optional plant filter for metadata.
        top_k: Number of documents to retrieve.

    Returns:
        Dict with context, documents, doc_count, confidence_boost.
    """
    # Step 1 — Retrieve relevant documents
    documents = retrieve_relevant_documents(
        question=question,
        plant_id=plant_id,
        top_k=top_k,
    )

    # Step 2 — Build context block
    if not documents:
        log_rag("No relevant documents found for query.")
        return {
            "context": "",
            "documents": [],
            "doc_count": 0,
            "confidence_boost": 0.0,
        }

    context_parts = []
    for i, doc in enumerate(documents, 1):
        meta = doc.get("metadata", {})
        doc_type = meta.get("doc_type", "Unknown")
        relevance = doc.get("relevance_score", 0)
        context_parts.append(
            f"[{i}] ({doc_type} | relevance: {relevance:.0%})\n"
            f"    {doc['content']}"
        )

    context = "\n\n".join(context_parts)

    # Step 3 — Compute confidence boost
    avg_relevance = sum(d["relevance_score"] for d in documents) / len(documents)
    confidence_boost = round(min(0.15, avg_relevance * 0.15), 4)

    log_rag(
        f"Retrieved {len(documents)} docs | "
        f"avg_relevance={avg_relevance:.2f} | "
        f"confidence_boost={confidence_boost}"
    )

    return {
        "context": context,
        "documents": documents,
        "doc_count": len(documents),
        "confidence_boost": confidence_boost,
    }


def _call_ollama(prompt: str) -> str:
    """
    Send prompt to Ollama (Mistral) and return generated text.
    Fully local, zero cost, no API keys needed.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT,
        )
        data = response.json()
        return data.get("response", "LLM returned empty response")
    except Exception as e:
        return f"Ollama call failed: {str(e)}"


def ask_with_rag(question: str, plant_id: int = None, top_k: int = 5) -> dict:
    """
    Full standalone RAG pipeline:
      ChromaDB retrieval -> Enriched prompt -> Ollama (Mistral) -> Grounded answer.

    This is the self-contained RAG function that does not
    depend on the orchestrator. Use this for direct RAG queries.

    Args:
        question: User's natural language question.
        plant_id: Optional plant filter.
        top_k: Number of context documents.

    Returns:
        Dict with:
          - answer: Ollama-generated grounded response
          - context: retrieved context block
          - doc_count: number of supporting documents
          - confidence_boost: retrieval quality score
          - model: Ollama model used
    """
    # Step 1 — Retrieve context
    rag_result = run_rag(question, plant_id=plant_id, top_k=top_k)
    context = rag_result.get("context", "")

    # Step 2 — Build enriched prompt
    if context:
        prompt = (
            f"You are an AI operations analyst for a solar energy platform.\n\n"
            f"Relevant Historical Data:\n{context}\n\n"
            f"User Question: {question}\n\n"
            f"Based on the historical data above, provide a detailed, "
            f"grounded analysis. Reference specific incidents when relevant."
        )
    else:
        prompt = (
            f"You are an AI operations analyst for a solar energy platform.\n\n"
            f"User Question: {question}\n\n"
            f"No historical data was found for this query. "
            f"Provide a general analysis based on your knowledge."
        )

    # Step 3 — Generate answer via Ollama
    log_rag(f"Sending to Ollama ({OLLAMA_MODEL}) with {rag_result['doc_count']} context docs ...")
    answer = _call_ollama(prompt)

    log_rag(f"Ollama response received ({len(answer)} chars)")

    return {
        "answer": answer,
        "context": context,
        "doc_count": rag_result["doc_count"],
        "confidence_boost": rag_result["confidence_boost"],
        "model": OLLAMA_MODEL,
    }

