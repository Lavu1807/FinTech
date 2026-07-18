"""
Pydantic schemas for the Visualization Agent.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class ChartMetadata(BaseModel):
    chart_id: str = Field(description="Unique identifier for the chart.")
    chart_title: str
    chart_type: str
    x_axis: str
    y_axis: str
    aggregation: str
    sorting: str
    filters: str = Field(default="None")
    description: str = Field(description="Accessibility alt text describing the chart.")
    business_purpose: str = Field(description="Why this chart is useful.")
    source_analysis: str = Field(description="The analysis type from the planner that triggered this chart.")
    confidence: float = Field(default=1.0)
    file_path: Optional[str] = None
    svg_file_path: Optional[str] = None

class VisualizationResult(BaseModel):
    charts: List[ChartMetadata]
    tableau_export_path: str
