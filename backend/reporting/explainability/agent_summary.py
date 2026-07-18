from typing import Dict, Any
from backend.state.state import FinSightState


def extract_agent_summaries(state: FinSightState) -> Dict[str, Any]:
    """
    Extracts qualitative summaries from the graph execution for explainability.
    """
    summaries = {}

    # 1. Planner Reasoning
    workflow_tracking = state.get("workflow_tracking", {})
    summaries["planner_reasoning"] = workflow_tracking.get("planner_reasoning", [])
    summaries["analysis_plan"] = workflow_tracking.get("analysis_plan", [])

    # 2. Validation Summary
    validation = state.get("validation", {})
    validation_results = validation.get("validation_results", [])
    if isinstance(validation_results, list):
        summaries["validation_checks"] = [
            {
                "insight": v.get("insight"),
                "status": v.get("status"),
                "notes": v.get("validation_notes", ""),
            }
            for v in validation_results
            if isinstance(v, dict)
        ]
    else:
        summaries["validation_checks"] = []

    # 3. Visualization Summary
    visualization = state.get("visualization", {})
    charts = visualization.get("charts", [])
    if isinstance(charts, list):
        summaries["visualization_summary"] = [
            {
                "chart_title": c.get("chart_title"),
                "description": c.get("description"),
                "file_path": c.get("file_path"),
            }
            for c in charts
            if isinstance(c, dict)
        ]
    else:
        summaries["visualization_summary"] = []

    # 4. Report Summary
    ai_insights = state.get("ai_insights", {})
    summaries["executive_summary"] = ai_insights.get("executive_summary", "")
    if isinstance(summaries["executive_summary"], dict):
        summaries["executive_summary"] = summaries["executive_summary"].get(
            "executive_summary", ""
        )

    return summaries
