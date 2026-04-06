"""
Phase 12 — Ingestion Pipeline

Reads operational data from all phases, converts to structured
documents, embeds them, and stores in the ChromaDB vector store.

Sources:
  - Phase 11: alerts.json
  - Phase 6:  evaluation_report.json
  - Phase 4:  prediction_logs.json
  - Phase 10: simulation_logs.json
"""

import json
import os

from phase_12_vector_rag.config import BASE_DIR, MAX_PREDICTION_LOGS
from phase_12_vector_rag.document_schemas import (
    AlertRecord,
    EvaluationReport,
    OperationalLog,
    SimulationResult,
)
from phase_12_vector_rag.embedding_model import encode_batch
from phase_12_vector_rag.vector_store import add_documents
from phase_12_vector_rag.utils import log_rag


def _load_json(path: str):
    """Safely load a JSON file."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _ingest_batch(documents: list) -> int:
    """Embed and store a batch of BaseDocument instances."""
    if not documents:
        return 0

    ids = [doc.doc_id for doc in documents]
    contents = [doc.content for doc in documents]
    metadatas = [doc.to_document()["metadata"] for doc in documents]
    embeddings = encode_batch(contents)

    return add_documents(ids, contents, embeddings, metadatas)


# ============================
# Source-specific ingestors
# ============================

def ingest_alerts() -> int:
    """Ingest alert records from Phase 11."""
    path = os.path.join(BASE_DIR, "phase_11_alerting", "alerts.json")
    data = _load_json(path)
    if not data:
        return 0

    docs = []
    for entry in data:
        alert = entry.get("alert", entry)
        content = (
            f"Alert {alert.get('alert_id', 'unknown')} at "
            f"{alert.get('timestamp', entry.get('logged_at', 'unknown'))}: "
            f"Severity {alert.get('severity', 'N/A')}, "
            f"Priority {alert.get('priority', 'N/A')}, "
            f"Plant {alert.get('plant_id', 1)}. "
            f"Decision: {alert.get('decision', 'N/A')}. "
            f"Message: {alert.get('message', 'N/A')}. "
            f"Context: {json.dumps(alert.get('context', {}))}"
        )
        docs.append(AlertRecord(
            content=content,
            plant_id=alert.get("plant_id", 1),
            timestamp=alert.get("timestamp", entry.get("logged_at", "")),
            metadata={"severity": alert.get("severity", ""), "alert_id": alert.get("alert_id", "")},
        ))

    return _ingest_batch(docs)


def ingest_evaluation_report() -> int:
    """Ingest model evaluation report from Phase 6."""
    path = os.path.join(BASE_DIR, "phase_06_evaluation", "evaluation_report.json")
    data = _load_json(path)
    if not data:
        return 0

    content = f"Model Evaluation Report: {json.dumps(data, indent=2)}"
    doc = EvaluationReport(
        content=content,
        metadata={"source": "phase_06_evaluation"},
    )
    return _ingest_batch([doc])


def ingest_prediction_logs() -> int:
    """Ingest recent prediction logs from Phase 4 MLOps."""
    path = os.path.join(BASE_DIR, "phase_04_mlops", "logging", "prediction_logs.json")
    data = _load_json(path)
    if not data:
        return 0

    docs = []
    for entry in data[-MAX_PREDICTION_LOGS:]:
        content = (
            f"Prediction log at {entry.get('timestamp', 'unknown')}: "
            f"Endpoint {entry.get('endpoint', 'N/A')}, "
            f"DC_POWER={entry.get('dc_power', 'N/A')}, "
            f"AC_POWER={entry.get('ac_power', 'N/A')}, "
            f"Prediction={entry.get('prediction', 'N/A')}, "
            f"Status={entry.get('status', 'N/A')}, "
            f"Model={entry.get('model_version', 'N/A')}"
        )
        docs.append(OperationalLog(
            content=content,
            timestamp=entry.get("timestamp", ""),
            metadata={"endpoint": entry.get("endpoint", ""), "status": entry.get("status", "")},
        ))

    return _ingest_batch(docs)


def ingest_simulation_logs() -> int:
    """Ingest scenario simulation logs from Phase 10."""
    path = os.path.join(BASE_DIR, "phase_10_scenario_engine", "simulation_logs.json")
    data = _load_json(path)
    if not data:
        return 0

    docs = []
    for entry in data:
        content = f"Simulation event: {json.dumps(entry)}"
        docs.append(SimulationResult(
            content=content,
            timestamp=entry.get("timestamp", ""),
            metadata={"source": "phase_10_scenario_engine"},
        ))

    return _ingest_batch(docs)


def ingest_single_document(doc_type: str, content: str, plant_id: int = 1, metadata: dict = None) -> int:
    """
    Ingest a single document in real-time.
    For use during live operations.

    Args:
        doc_type: One of 'AlertRecord', 'SimulationResult', 'EvaluationReport', 'OperationalLog'.
        content: Text content.
        plant_id: Plant ID.
        metadata: Extra metadata dict.
    """
    schema_map = {
        "AlertRecord": AlertRecord,
        "SimulationResult": SimulationResult,
        "EvaluationReport": EvaluationReport,
        "OperationalLog": OperationalLog,
    }
    cls = schema_map.get(doc_type, OperationalLog)
    doc = cls(content=content, plant_id=plant_id, metadata=metadata or {})
    return _ingest_batch([doc])


def run_full_ingestion() -> dict:
    """
    Run the complete ingestion pipeline across all data sources.
    Call at application startup.

    Returns:
        Dict of counts per source.
    """
    log_rag("Starting full ingestion pipeline ...")

    counts = {
        "alerts": ingest_alerts(),
        "evaluation_report": ingest_evaluation_report(),
        "prediction_logs": ingest_prediction_logs(),
        "simulation_logs": ingest_simulation_logs(),
    }

    total = sum(counts.values())
    log_rag(f"Ingestion complete — {total} new documents added: {counts}")
    return counts
