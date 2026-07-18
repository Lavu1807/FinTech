"""
Generates the core Markdown report from the FinSightState using Jinja2 templates.
"""
import os
from datetime import datetime, timezone
from typing import Dict
from jinja2 import Environment, FileSystemLoader
from backend.state.state import FinSightState


def _extract_column_types(state: FinSightState) -> Dict[str, int]:
    """Extract column type counts from the dataset profile."""
    profile = state.get("dataset_profile", {})
    col_details = profile.get("column_details", {})
    type_counts: Dict[str, int] = {}
    for col_name, col_info in col_details.items():
        dtype = str(col_info.get("dtype", "unknown"))
        type_counts[dtype] = type_counts.get(dtype, 0) + 1
    return type_counts


def generate_markdown(state: FinSightState, filename: str = "dataset") -> str:
    """Render the executive.md Jinja2 template against the full FinSightState."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Setup Jinja2 Environment
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template('executive.md')

    # Extract state sections
    dataset_info = state.get("dataset_info", {})
    profile = state.get("dataset_profile", {}).get("overview", {})
    quality = state.get("quality_metrics", {})
    cleaning = state.get("cleaning_results", {}).get("cleaning_recommendations", [])
    analytics = state.get("business_analytics", {})
    insights = state.get("ai_insights", {})
    validation_obj = state.get("validation", {})
    validation_results = validation_obj.get("validation_results", [])
    viz = state.get("visualization", {}).get("charts", [])
    meta = state.get("execution_metadata", {})
    workflow = state.get("workflow_tracking", {})
    dataset_risks = state.get("dataset_risks", [])
    agent_logs = state.get("agent_logs", [])
    timeline = meta.get("timeline", [])
    column_types = _extract_column_types(state)

    # Render template
    md_content = template.render(
        filename=filename,
        now=now,
        dataset_info=dataset_info,
        profile=profile,
        quality=quality,
        cleaning=cleaning,
        analytics=analytics,
        insights=insights,
        validation_obj=validation_obj,
        validation_results=validation_results,
        viz=viz,
        meta=meta,
        workflow=workflow,
        dataset_risks=dataset_risks,
        agent_logs=agent_logs,
        timeline=timeline,
        column_types=column_types
    )

    return md_content
