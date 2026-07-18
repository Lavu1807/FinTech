"""
Advanced Analytics LangGraph Node.
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any

from backend.state.state import FinSightState, AgentLog
from backend.utils.logger import logger

from .schemas import AnalyticsResult
from .kpi_engine import KPIRegistry
from .trend_engine import analyze_trends
from .segmentation import analyze_segments
from .statistical_analysis import compute_statistics
from .anomaly_detection import detect_anomalies
from .exporter import export_analytics


def analytics_node(state: FinSightState) -> Dict[str, Any]:
    """LangGraph node execution block."""
    start_time = time.time()
    agent_name = "Analytics Agent"

    df = state.get("cleaning_results", {}).get("cleaned_dataframe")
    if df is None:
        df = state.get("dataset_info", {}).get("raw_dataframe")
        logger.warning(
            f"{agent_name}: 'cleaned_dataframe' missing. Falling back to 'raw_dataframe'."
        )

    if df is None or df.empty:
        logger.error(f"{agent_name}: Empty dataframe.")
        return {
            "agent_logs": [
                {
                    "agent_name": agent_name,
                    "status": "FAILED",
                    "timestamp": datetime.now(timezone.utc),
                    "message": "Empty dataframe.",
                    "provider_used": "Pandas",
                    "llm_calls": 0,
                    "estimated_tokens": 0,
                    "estimated_cost": 0.0,
                    "warnings": [],
                }
            ]
        }

    workflow_tracking = state.get("workflow_tracking", {})
    analysis_plan = [a.lower() for a in workflow_tracking.get("analysis_plan", [])]
    run_all = len(analysis_plan) == 0

    # KPIs using Registry
    kpis = {}
    if run_all or any("kpi" in a or "metric" in a for a in analysis_plan):
        registry = KPIRegistry()
        kpis = registry.execute_all(df)

    # Rest of computations based on Planner Plan
    plan_str = " ".join(analysis_plan)
    trends = analyze_trends(df) if (run_all or "trend" in plan_str) else {}
    segments = (
        analyze_segments(df)
        if (run_all or "segment" in plan_str or "compar" in plan_str)
        else {}
    )
    stats = (
        compute_statistics(df)
        if (run_all or "stat" in plan_str or "correl" in plan_str)
        else {}
    )
    anomalies = (
        detect_anomalies(df)
        if (run_all or "anomal" in plan_str or "outlier" in plan_str)
        else []
    )

    # Visualization Recommendations
    vis_recs = []
    if trends:
        vis_recs.append(
            "Recommend visualizing trends over time using line charts to track growth."
        )
    if segments:
        top_keys = list(segments.keys())[:3]
        vis_recs.append(
            f"Recommend visualizing segmentation for key dimensions ({', '.join(top_keys)}) using bar charts."
        )
    if anomalies:
        vis_recs.append(
            "Recommend highlighting detected anomalies using scatter plots."
        )

    result = AnalyticsResult(
        calculated_kpis=kpis,
        trend_analysis=trends,
        segment_analysis=segments,
        statistical_analysis=stats,
        anomaly_summary=anomalies,
        visualization_recommendations=vis_recs,
        generated_exports=[],
        chart_paths=[],
    )

    # Exporter
    workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
    exports = export_analytics(result, workflow_id)
    result.generated_exports = exports

    log: AgentLog = {
        "agent_name": agent_name,
        "status": "COMPLETED",
        "timestamp": datetime.now(timezone.utc),
        "message": f"Computed advanced analytics with {len(kpis)} KPIs, {len(stats)} statistical metrics, and {len(anomalies)} anomalies.",
        "provider_used": "Deterministic (Pandas)",
        "llm_calls": 0,
        "estimated_tokens": 0,
        "estimated_cost": 0.0,
        "warnings": anomalies,
    }

    return {
        "business_analytics": result.model_dump(),
        "workflow_tracking": {
            **workflow_tracking,
            "current_agent": agent_name,
            "completed_agents": workflow_tracking.get("completed_agents", [])
            + [agent_name],
            "execution_time": time.time() - start_time,
        },
        "agent_logs": [log],
    }
