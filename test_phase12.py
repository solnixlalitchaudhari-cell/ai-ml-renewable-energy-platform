"""Phase 12 — Production Vector RAG Test Suite (ChromaDB)"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import shutil

# ========== SETUP: Clean vector store for fresh test ==========
VECTOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vector_store_test")

# Remove stale test DB from previous runs BEFORE ChromaDB initializes
if os.path.exists(VECTOR_DIR):
    shutil.rmtree(VECTOR_DIR, ignore_errors=True)
os.makedirs(VECTOR_DIR, exist_ok=True)

# Temporarily override config to use test directory
import phase_12_vector_rag.config as cfg
cfg.CHROMA_PERSIST_DIR = VECTOR_DIR

# Force re-init of vector store with test directory
import importlib
import phase_12_vector_rag.vector_store as vs
importlib.reload(vs)

# ========== TEST 1: Embedding Model ==========
print("TEST 1: Embedding model")
from phase_12_vector_rag.embedding_model import encode_text, encode_batch

emb = encode_text("test solar power alert")
assert len(emb) == 384, f"Expected 384 dims, got {len(emb)}"
print(f"  single embed: {len(emb)} dims")

batch = encode_batch(["hello world", "solar energy"])
assert len(batch) == 2
assert len(batch[0]) == 384
print(f"  batch embed: {len(batch)} vectors of {len(batch[0])} dims")
print("  PASSED\n")

# ========== TEST 2: Document Schemas ==========
print("TEST 2: Document schemas")
from phase_12_vector_rag.document_schemas import AlertRecord, EvaluationReport

alert = AlertRecord(content="CRITICAL P0 alert at plant 1", plant_id=1)
doc = alert.to_document()
assert doc["type"] == "AlertRecord"
assert doc["plant_id"] == 1
assert len(doc["id"]) == 16  # hash-based ID
print(f"  AlertRecord id: {doc['id']}")
print(f"  type: {doc['type']}, plant_id: {doc['plant_id']}")

# Duplicate prevention — same content = same ID
alert2 = AlertRecord(content="CRITICAL P0 alert at plant 1", plant_id=1)
assert alert.doc_id == alert2.doc_id
print(f"  duplicate detection: same content -> same ID [OK]")
print("  PASSED\n")

# ========== TEST 3: Vector Store CRUD ==========
print("TEST 3: Vector store operations")
from phase_12_vector_rag.vector_store import add_documents, query, get_stats

ids = ["test_001", "test_002", "test_003"]
docs = [
    "CRITICAL P0 alert: inverter failure at plant 1",
    "Normal operation: all systems green at plant 2",
    "WARNING: drift detected in DC_POWER sensor",
]
embs = encode_batch(docs)
metas = [
    {"doc_type": "AlertRecord", "plant_id": "1", "timestamp": "2025-01-01"},
    {"doc_type": "OperationalLog", "plant_id": "2", "timestamp": "2025-01-02"},
    {"doc_type": "AlertRecord", "plant_id": "1", "timestamp": "2025-01-03"},
]

added = add_documents(ids, docs, embs, metas)
assert added == 3, f"Expected 3 added, got {added}"
print(f"  added: {added} documents")

# Test duplicate prevention
added_again = add_documents(ids, docs, embs, metas)
assert added_again == 0, f"Expected 0 duplicates, got {added_again}"
print(f"  duplicate add: {added_again} (correctly prevented)")
print("  PASSED\n")

# ========== TEST 4: Metadata-Filtered Query ==========
print("TEST 4: Metadata-filtered query")
q_emb = encode_text("Have we seen critical alerts before?")

# Unfiltered
results_all = query(q_emb, top_k=3)
assert len(results_all["ids"][0]) > 0
print(f"  unfiltered results: {len(results_all['ids'][0])}")

# Filter by plant_id
results_p1 = query(q_emb, top_k=3, filters={"plant_id": "1"})
for meta in results_p1["metadatas"][0]:
    assert meta["plant_id"] == "1"
print(f"  plant_id=1 results: {len(results_p1['ids'][0])}")

# Filter by doc_type
results_alert = query(q_emb, top_k=3, filters={"doc_type": "AlertRecord"})
for meta in results_alert["metadatas"][0]:
    assert meta["doc_type"] == "AlertRecord"
print(f"  AlertRecord results: {len(results_alert['ids'][0])}")
print("  PASSED\n")

# ========== TEST 5: Stats ==========
print("TEST 5: Vector store stats")
stats = get_stats()
assert stats["total_documents"] == 3
assert stats["health"] == "healthy"
assert "AlertRecord" in stats["documents_per_type"]
print(f"  total: {stats['total_documents']}")
print(f"  types: {stats['documents_per_type']}")
print(f"  health: {stats['health']}")
print("  PASSED\n")

# ========== TEST 6: Retriever ==========
print("TEST 6: Retriever with relevance scoring")
from phase_12_vector_rag.retriever import retrieve_relevant_documents

docs_found = retrieve_relevant_documents("Have we seen similar CRITICAL alerts?", plant_id=1)
assert len(docs_found) > 0, "Expected at least 1 retrieved document"
for d in docs_found:
    assert "content" in d
    assert "relevance_score" in d
    assert d["relevance_score"] >= 0
print(f"  retrieved: {len(docs_found)} docs")
print(f"  top relevance: {docs_found[0]['relevance_score']}")
print(f"  top content preview: {docs_found[0]['content'][:60]}...")
print("  PASSED\n")

# ========== TEST 7: RAG Engine ==========
print("TEST 7: RAG engine full pipeline")
from phase_12_vector_rag.rag_engine import run_rag

rag = run_rag("What happened with critical alerts at plant 1?", plant_id=1)
assert rag["doc_count"] > 0
assert len(rag["context"]) > 0
assert rag["confidence_boost"] >= 0.0
print(f"  doc_count: {rag['doc_count']}")
print(f"  confidence_boost: {rag['confidence_boost']}")
print(f"  context length: {len(rag['context'])} chars")
print(f"  context preview:\n    {rag['context'][:120]}...")
print("  PASSED\n")

# ========== TEST 8: Graceful empty ==========
print("TEST 8: Graceful handling of unrelated query")
rag2 = run_rag("What is quantum physics?", plant_id=99)
assert isinstance(rag2, dict)
assert "context" in rag2
print(f"  doc_count: {rag2['doc_count']}")
print(f"  confidence_boost: {rag2['confidence_boost']}")
print("  PASSED\n")

# ========== CLEANUP ==========
try:
    shutil.rmtree(VECTOR_DIR)
    print("[Cleanup] Test vector store removed.")
except Exception:
    pass

print("=" * 55)
print("ALL TESTS PASSED — Phase 12 Production RAG is operational")
print("=" * 55)
