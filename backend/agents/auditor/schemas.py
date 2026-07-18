"""
Pydantic schemas for the Data Auditor Agent.
Ensures strong typing of all profiling metrics before updating the state or exporting to JSON.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel


class DatasetOverview(BaseModel):
    filename: str
    dataset_shape: Tuple[int, int]
    row_count: int
    column_count: int
    memory_usage_bytes: int
    memory_usage_mb: float
    size_category: str  # "Small", "Medium", "Large"
    duplicate_rows: int
    duplicate_percentage: float


class DatasetRisk(BaseModel):
    risk_level: str
    risk_type: str
    affected_columns: List[str]
    recommendation: str


class OutlierReport(BaseModel):
    column: str
    number_of_outliers: int
    percentage: float
    recommended_action: str


class ColumnProfile(BaseModel):
    name: str
    datatype: str
    nullable: bool
    unique_values: int
    unique_percentage: float
    missing_values: int
    missing_percentage: float
    duplicate_values: int
    cardinality: str  # "Low", "Medium", "High"
    inferred_semantic_type: str

    # Conditional Analytics
    numerical_stats: Optional[Dict[str, Any]] = None
    categorical_stats: Optional[Dict[str, Any]] = None
    date_stats: Optional[Dict[str, Any]] = None
    outliers: Optional[OutlierReport] = None


class QualityScore(BaseModel):
    missing_value_score: float
    duplicate_score: float
    outlier_score: float
    consistency_score: float
    completeness_score: float
    overall_score: float
    quality_grade: str
    explanations: Dict[str, str]


class CleaningRecommendation(BaseModel):
    column: str
    issue: str
    severity: str  # "High", "Medium", "Low"
    recommended_action: str
    reason: str
    expected_impact: str
