"""
Pydantic schemas for the AI Insight Agent.
Structured output models that the LLM is forced to return via the Gateway.
"""

from pydantic import BaseModel, Field
from typing import List


class KeyFinding(BaseModel):
    headline: str = Field(description="Short headline of the finding.")
    explanation: str = Field(description="Detailed explanation grounded in evidence.")
    business_impact: str = Field(description="Why this matters to the business.")
    priority: str = Field(description="Immediate / High / Medium / Low")
    supporting_metrics: str = Field(
        description="Exact KPI values from the analytics that support this claim."
    )
    affected_dimensions: str = Field(
        default="",
        description="Business dimensions affected (e.g., Revenue, Customer, Inventory).",
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0 based on evidence strength."
    )


class Risk(BaseModel):
    risk_type: str = Field(description="Category of risk.")
    severity: str = Field(description="Low / Medium / High / Critical")
    likelihood: str = Field(default="Medium", description="Low / Medium / High")
    business_impact: str = Field(description="Concrete impact on the business.")
    mitigation: str = Field(description="Recommended mitigation strategy.")
    recommended_action: str = Field(description="Specific action to take.")
    supporting_evidence: str = Field(
        default="", description="KPI or metric supporting this risk."
    )
    confidence: float = Field(description="Confidence score 0.0-1.0.")


class Opportunity(BaseModel):
    headline: str = Field(description="Short headline of the opportunity.")
    explanation: str = Field(description="Detailed explanation of the opportunity.")
    opportunity_type: str = Field(
        default="General",
        description="Revenue / Cost Reduction / Customer / Retention / Operational",
    )
    business_impact: str = Field(default="", description="Expected business impact.")
    supporting_metrics: str = Field(
        description="Exact KPI values supporting this opportunity."
    )
    confidence: float = Field(description="Confidence score 0.0-1.0.")


class Recommendation(BaseModel):
    horizon: str = Field(description="Immediate / Medium-term / Long-term")
    recommendation: str = Field(description="The recommendation.")
    reason: str = Field(description="Why this recommendation matters.")
    expected_impact: str = Field(description="Expected outcome if implemented.")
    difficulty: str = Field(default="Medium", description="Low / Medium / High")
    priority: str = Field(description="Immediate / High / Medium / Low")
    supporting_metrics: str = Field(
        default="", description="Evidence supporting this recommendation."
    )
    confidence: float = Field(description="Confidence score 0.0-1.0.")


class NextBestAction(BaseModel):
    action: str = Field(description="Specific action to take.")
    reason: str = Field(default="", description="Why this action is recommended.")
    expected_benefit: str = Field(description="Expected benefit if executed.")
    priority: str = Field(default="High", description="Immediate / High / Medium / Low")
    estimated_urgency: str = Field(
        description="Immediate / This Week / This Month / This Quarter"
    )
    supporting_evidence: str = Field(
        default="", description="Evidence grounding this action."
    )
    confidence: float = Field(description="Confidence score 0.0-1.0.")


class InsightOutput(BaseModel):
    executive_summary: str = Field(
        description="A high-level executive summary (under 250 words) of the business situation covering health, opportunities, risks, and quality."
    )
    key_findings: List[KeyFinding] = Field(
        description="List of primary factual findings derived from KPIs and trends. Must be evidence-backed."
    )
    business_risks: List[Risk] = Field(
        description="List of identified business and operational risks."
    )
    business_opportunities: List[Opportunity] = Field(
        description="List of strategic opportunities."
    )
    recommendations: List[Recommendation] = Field(
        description="Recommendations spanning Immediate, Medium-term, and Long-term horizons."
    )
    next_best_actions: List[NextBestAction] = Field(
        description="Immediate actionable tasks for the operations team."
    )
    data_quality_observations: List[str] = Field(
        default_factory=list,
        description="Observations regarding missing data or quality defects.",
    )
    confidence: float = Field(
        description="Overall confidence score (0.0 to 1.0) based on data quality and completeness."
    )
