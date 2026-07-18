"""
Pydantic schemas for Advanced Analytics Agent.
"""

from pydantic import BaseModel
from typing import Dict, Any, List


class AnalyticsResult(BaseModel):
    calculated_kpis: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    segment_analysis: Dict[str, Any]
    statistical_analysis: Dict[str, Any]
    anomaly_summary: List[str]
    visualization_recommendations: List[str]
    generated_exports: List[str]
    chart_paths: List[str]
