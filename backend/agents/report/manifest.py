"""
Manifest generator for the Report Agent.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.state.state import FinSightState


def generate_manifest(state: FinSightState, exported_files: List[str]) -> Dict[str, Any]:
    """Generate report_manifest.json with full workflow metadata."""
    meta = state.get("execution_metadata", {})
    workflow = state.get("workflow_tracking", {})
    validation = state.get("validation", {})
    charts = state.get("visualization", {}).get("charts", [])

    # Determine which sections were successfully included
    sections = ["Executive Summary", "Dataset Overview", "Data Quality Assessment"]

    analytics = state.get("business_analytics", {})
    if analytics.get("calculated_kpis"):
        sections.append("Business KPIs")
    if analytics.get("trend_analysis"):
        sections.append("Trend Analysis")
    if analytics.get("segment_analysis"):
        sections.append("Segmentation Analysis")
    if analytics.get("statistical_analysis"):
        sections.append("Statistical Analysis")
    if analytics.get("anomaly_summary"):
        sections.append("Detected Anomalies")

    insights = state.get("ai_insights", {})
    if insights.get("business_risks"):
        sections.append("Detected Risks")
    if insights.get("business_opportunities"):
        sections.append("Business Opportunities")
    if insights.get("recommendations"):
        sections.append("Recommendations")
    if insights.get("next_best_actions"):
        sections.append("Next Best Actions")
    if validation.get("validation_results"):
        sections.append("Validation Summary")
    if charts:
        sections.append("Charts")

    sections.extend(["Workflow Execution", "Appendix"])

    return {
        "workflow_id": workflow.get("workflow_id", "unknown"),
        "dataset_name": state.get("dataset_info", {}).get("filename", "unknown"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_version": "2.0.0",
        "workflow_version": "1.0.0",
        "prompt_version": meta.get("prompt_version", "v3.0"),
        "execution_time": meta.get("latency", 0),
        "chart_count": len(charts),
        "validation_status": validation.get("overall_status", "N/A"),
        "overall_confidence": validation.get("average_confidence", 0.0),
        "included_sections": sections,
        "generated_files": exported_files
    }
