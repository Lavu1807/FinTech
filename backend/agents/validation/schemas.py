"""
Pydantic schemas for the Validation Agent.
"""

from pydantic import BaseModel, Field
from typing import List


class ValidationScore(BaseModel):
    """Validation result for one insight."""

    insight: str
    status: str = "PASSED"
    confidence_score: float = 1.0
    hallucination_score: float = 0.0
    consistency_score: float = 1.0
    coverage_score: float = 1.0
    evidence_score: float = 1.0
    supporting_metrics: List[str] = Field(default_factory=list)
    evidence_sources: List[str] = Field(default_factory=list)
    validation_notes: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ValidationSummary(BaseModel):
    """Aggregate summary across all validated insights."""

    total_insights: int
    passed: int
    failed: int
    warning_count: int
    overall_status: str
    average_confidence: float
    average_evidence_score: float
    hallucination_rate: float
    unsupported_claims: List[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    """Full validation report combining per-insight results and summary."""

    summary: ValidationSummary
    scores: List[ValidationScore]
