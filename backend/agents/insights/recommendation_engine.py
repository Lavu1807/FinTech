"""
Recommendation Engine for AI Insight Agent.
Sorts recommendations by priority and calculates deterministic confidence override.
"""
from typing import Any
from backend.state.state import FinSightState
from .schemas import InsightOutput


# Priority ordering for sorting
_PRIORITY_ORDER = {"Immediate": 0, "High": 1, "Medium": 2, "Low": 3}


def _sort_key(item: Any) -> int:
    """Extract priority sort key from any Pydantic model with a 'priority' field."""
    priority = getattr(item, 'priority', 'Medium')
    return _PRIORITY_ORDER.get(priority, 2)


def process_recommendations(insight: InsightOutput) -> InsightOutput:
    """Sort all recommendation-like lists by priority (Immediate first)."""
    insight.recommendations = sorted(insight.recommendations, key=_sort_key)
    insight.next_best_actions = sorted(insight.next_best_actions, key=_sort_key)
    insight.key_findings = sorted(insight.key_findings, key=_sort_key)
    return insight


def calculate_deterministic_confidence(insight: InsightOutput, state: FinSightState) -> float:
    """
    Override the LLM's self-reported confidence with a deterministic calculation.
    
    Factors:
    1. Planner confidence (25%)
    2. Data quality score (25%)  
    3. Number of supporting metrics across all findings (25%)
    4. Validation readiness — presence of actionable outputs (25%)
    """
    workflow = state.get("workflow_tracking", {})
    quality = state.get("quality_metrics", {})

    # 1. Planner confidence
    planner_conf = 0.5
    try:
        planner_conf = float(workflow.get("planner_confidence", 0.5))
    except (ValueError, TypeError):
        pass

    # 2. Data quality score — map grades to numeric
    grade_map = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "F": 0.2}
    quality_score = grade_map.get(quality.get("quality_grade", "C"), 0.6)

    # 3. Metric density — how many findings/risks/opportunities have supporting evidence
    total_items = (
        len(insight.key_findings)
        + len(insight.business_risks)
        + len(insight.business_opportunities)
        + len(insight.recommendations)
    )
    items_with_evidence = 0
    for f in insight.key_findings:
        if f.supporting_metrics and f.supporting_metrics != "Insufficient evidence.":
            items_with_evidence += 1
    for r in insight.business_risks:
        if r.supporting_evidence and r.supporting_evidence != "Insufficient evidence.":
            items_with_evidence += 1
    for o in insight.business_opportunities:
        if o.supporting_metrics and o.supporting_metrics != "Insufficient evidence.":
            items_with_evidence += 1
    for rec in insight.recommendations:
        if rec.supporting_metrics and rec.supporting_metrics != "Insufficient evidence.":
            items_with_evidence += 1

    metric_density = (items_with_evidence / total_items) if total_items > 0 else 0.5

    # 4. Validation readiness — are there actionable outputs?
    readiness = 1.0 if (
        len(insight.key_findings) >= 1
        and len(insight.recommendations) >= 1
        and len(insight.next_best_actions) >= 1
    ) else 0.5

    # Weighted combination
    deterministic_conf = (
        planner_conf * 0.25
        + quality_score * 0.25
        + metric_density * 0.25
        + readiness * 0.25
    )

    return round(min(max(deterministic_conf, 0.0), 1.0), 3)
