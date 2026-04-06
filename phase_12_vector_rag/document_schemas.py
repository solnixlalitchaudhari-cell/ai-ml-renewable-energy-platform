"""
Phase 12 — Document Schemas

Typed document models for all data sources that flow
into the vector store:
  - EvaluationReport
  - SimulationResult
  - AlertRecord
  - OperationalLog

Each schema produces a dict with:  id, type, plant_id,
timestamp, content, metadata — ready for ChromaDB ingestion.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from phase_12_vector_rag.utils import generate_doc_id, format_timestamp


@dataclass
class BaseDocument:
    """Base class for all RAG document types."""
    content: str
    plant_id: int = 1
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = format_timestamp()

    @property
    def doc_type(self) -> str:
        return self.__class__.__name__

    @property
    def doc_id(self) -> str:
        return generate_doc_id(self.content)

    def to_document(self) -> dict:
        """Convert to a dict ready for ChromaDB ingestion."""
        return {
            "id": self.doc_id,
            "type": self.doc_type,
            "plant_id": self.plant_id,
            "timestamp": self.timestamp,
            "content": self.content,
            "metadata": {
                **self.metadata,
                "doc_type": self.doc_type,
                "plant_id": str(self.plant_id),
                "timestamp": self.timestamp,
            }
        }


@dataclass
class EvaluationReport(BaseDocument):
    """Model evaluation report from Phase 6."""
    pass


@dataclass
class SimulationResult(BaseDocument):
    """Scenario simulation result from Phase 10."""
    pass


@dataclass
class AlertRecord(BaseDocument):
    """Alert record from Phase 11 alerting system."""
    pass


@dataclass
class OperationalLog(BaseDocument):
    """Prediction / operational log from Phase 4 MLOps."""
    pass
