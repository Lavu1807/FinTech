"""
Pydantic models for the Planner Agent.
"""

from pydantic import BaseModel, Field
from typing import List


class PlannerOutput(BaseModel):
    dataset_type: str = Field(
        description="The inferred type of dataset (e.g., Transaction, Customer, Sales)."
    )
    business_domain: str = Field(
        description="The business domain this data belongs to."
    )
    analysis_plan: List[str] = Field(description="Ordered list of analyses to perform.")
    required_agents: List[str] = Field(
        description="List of downstream agents required."
    )
    execution_graph: List[str] = Field(
        description="The ordered agent execution graph (e.g., ['Planner', 'Data Auditor', ...])."
    )
    reasoning: List[str] = Field(
        description="List explaining WHY each analysis was selected."
    )
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")
