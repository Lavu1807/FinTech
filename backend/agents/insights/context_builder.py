"""
Context Builder for AI Insight Agent.
Extracts deterministic state and formats into structured sections for the LLM prompt.
"""
import json
from typing import Dict
from backend.state.state import FinSightState


def build_xml_context(state: FinSightState) -> Dict[str, str]:
    """
    Build a structured context dictionary from the FinSightState.
    Each key maps to a named placeholder in the prompt template.
    Only deterministic, pre-computed data is included. Never raw DataFrames.
    """
    dataset_info = state.get("dataset_info", {})
    quality_metrics = state.get("quality_metrics", {})
    dataset_risks = state.get("dataset_risks", [])
    analytics = state.get("business_analytics", {})
    workflow = state.get("workflow_tracking", {})
    profile = state.get("dataset_profile", {}).get("overview", {})

    # 1. Dataset Summary
    dataset_summary = json.dumps({
        "filename": dataset_info.get("filename", "unknown"),
        "category": dataset_info.get("dataset_category", "unknown"),
        "business_domain": dataset_info.get("business_domain", "unknown"),
        "rows": profile.get("rows", "unknown"),
        "columns": profile.get("cols", "unknown"),
        "memory_mb": profile.get("memory_mb", "unknown")
    }, indent=2)

    # 2. KPIs
    kpis = json.dumps(analytics.get("calculated_kpis", {}), indent=2)

    # 3. Trend Analysis
    trends = json.dumps(analytics.get("trend_analysis", {}), indent=2)

    # 4. Segment Analysis
    segments = json.dumps(analytics.get("segment_analysis", {}), indent=2)

    # 5. Statistical Findings
    stats = json.dumps(analytics.get("statistical_analysis", {}), indent=2)

    # 6. Detected Anomalies
    anomalies = json.dumps(analytics.get("anomaly_summary", []), indent=2)

    # 7. Data Quality
    quality = json.dumps({
        "quality_grade": quality_metrics.get("quality_grade", "N/A"),
        "scores": quality_metrics.get("scores", {}),
        "risks": dataset_risks
    }, indent=2)

    # 8. Planner Reasoning
    planner = json.dumps({
        "planner_reasoning": workflow.get("planner_reasoning", "No planner reasoning available."),
        "planner_confidence": workflow.get("planner_confidence", "N/A"),
        "analysis_plan": workflow.get("analysis_plan", [])
    }, indent=2)

    # 9. Business Domain
    domain = dataset_info.get("business_domain", "Unknown")

    # 10. Risk Level
    risk_level = quality_metrics.get("quality_grade", "N/A")

    return {
        "dataset_summary": dataset_summary,
        "kpis": kpis,
        "trend_analysis": trends,
        "segment_analysis": segments,
        "statistical_findings": stats,
        "detected_anomalies": anomalies,
        "data_quality": quality,
        "planner_reasoning": planner,
        "business_domain": domain,
        "risk_level": risk_level
    }
