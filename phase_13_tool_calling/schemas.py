"""
Phase 13 — Tool Schemas

Defines Pydantic schemas for the expected outputs of each tool.
Ensures tool execution returns structured, validated data.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class RiskAssessment(BaseModel):
    risk_level: str = Field(description="The risk level (e.g. LOW, MEDIUM, HIGH, CRITICAL)", default="LOW")
    estimated_financial_risk: float = Field(description="Estimated financial risk in rupees", default=0.0)

class RiskAssessmentOutput(BaseModel):
    risk_assessment: RiskAssessment

class OpsAnalysis(BaseModel):
    operational_risk: str = Field(description="The operational risk level", default="Low")
    reason: str = Field(description="Explanation of the operational risk", default="")

class OpsAnalysisOutput(BaseModel):
    ops_analysis: OpsAnalysis

class FinanceAnalysis(BaseModel):
    financial_risk: str = Field(description="The financial risk level", default="Low")
    impact: str = Field(description="Explanation of the financial impact", default="")

class FinanceAnalysisOutput(BaseModel):
    finance_analysis: FinanceAnalysis

class StrategySummaryOutput(BaseModel):
    strategy_summary: str = Field(description="Executive strategic recommendation", default="")

class DriftStatus(BaseModel):
    drift_risk: str = Field(description="Data drift risk level", default="LOW")

class DriftStatusOutput(BaseModel):
    drift_status: DriftStatus

class SimulationResult(BaseModel):
    metrics: Dict[str, Any]
    drift_status: Dict[str, Any]
    is_simulation: bool

class SimulationOutput(BaseModel):
    simulation_result: SimulationResult
