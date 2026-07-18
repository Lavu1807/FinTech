"""
The Data Auditor Agent.
Orchestrates the deterministic profiling, scoring, and recommendation process.
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any

from backend.state.state import FinSightState, AgentLog
from .profiler import generate_overview, profile_dataframe
from .quality import calculate_quality
from .recommendations import generate_recommendations, detect_risks
from backend.utils.logger import logger


def _generate_executive_summary(
    overview: Any, quality: Any, recommendations: Any
) -> str:
    """Generates a deterministic executive summary."""
    num_recs = len(recommendations)

    summary = (
        f"The dataset contains {overview.row_count} records across {overview.column_count} columns. "
        f"Exactly {overview.duplicate_rows} duplicate rows were found. "
        f"Overall quality score is {quality.overall_score}/100 (Grade {quality.quality_grade}). "
    )

    # Find biggest concern
    concerns = []
    if quality.missing_value_score < 90:
        concerns.append("missing values")
    if quality.outlier_score < 90:
        concerns.append("outliers")

    if concerns:
        summary += f"The largest concern is {', '.join(concerns)}. "

    summary += f"{num_recs} cleaning actions are recommended."
    return summary


def auditor_node(state: FinSightState) -> Dict[str, Any]:
    """
    Main LangGraph node for the Data Auditor Agent.
    """
    start_time = time.time()
    agent_name = "Data Auditor Agent"

    raw_df = state.get("dataset_info", {}).get("raw_dataframe")
    filename = state.get("dataset_info", {}).get("filename", "unknown_dataset.csv")

    if raw_df is None or raw_df.empty:
        logger.error("Data Auditor received empty dataframe.")
        return {
            "agent_logs": [
                {
                    "agent_name": agent_name,
                    "status": "FAILED",
                    "timestamp": datetime.now(timezone.utc),
                    "message": "No valid dataset provided.",
                }
            ]
        }

    try:
        # 1. Profile Dataset
        overview = generate_overview(raw_df, filename)
        column_profiles = profile_dataframe(raw_df)

        # 2. Quality, Recommendations & Risks
        quality_score = calculate_quality(column_profiles, overview.row_count)
        recs = generate_recommendations(column_profiles)
        risks = detect_risks(column_profiles)

        # 3. Export to JSON
        workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
        from backend.services.artifact_manager import ArtifactManager

        artifact_mgr = ArtifactManager(workflow_id)

        # Serialize Pydantic objects to dicts
        dataset_profile = {
            "overview": overview.model_dump(),
            "columns": {p.name: p.model_dump() for p in column_profiles},
        }
        quality_metrics = {
            "scores": quality_score.model_dump(exclude={"explanations"}),
            "explanations": quality_score.explanations,
        }
        cleaning_recs = [r.model_dump() for r in recs]
        risk_reports = [r.model_dump() for r in risks]

        artifact_mgr.save_json("profiling", "dataset_profile.json", dataset_profile)
        artifact_mgr.save_json("profiling", "quality_report.json", quality_metrics)
        artifact_mgr.save_json("profiling", "recommendations.json", cleaning_recs)
        artifact_mgr.save_json("profiling", "risks.json", risk_reports)

        # 4. Executive Summary
        exec_summary = _generate_executive_summary(overview, quality_score, recs)

        # 5. Update State
        workflow_tracking = state.get("workflow_tracking", {})
        completed_agents = workflow_tracking.get("completed_agents", []) + [agent_name]

        log: AgentLog = {
            "agent_name": agent_name,
            "status": "COMPLETED",
            "timestamp": datetime.now(timezone.utc),
            "message": exec_summary,
        }

        cleaning_results = state.get("cleaning_results", {})

        return {
            "dataset_profile": dataset_profile,
            "quality_metrics": quality_metrics,
            "dataset_risks": risk_reports,
            "cleaning_results": {
                **cleaning_results,
                "cleaning_recommendations": cleaning_recs,
            },
            "workflow_tracking": {
                **workflow_tracking,
                "current_agent": agent_name,
                "completed_agents": completed_agents,
                "execution_time": time.time() - start_time,
            },
            "agent_logs": [log],
        }

    except Exception as e:
        logger.error(f"Data Auditor Agent failed: {str(e)}")
        log: AgentLog = {
            "agent_name": agent_name,
            "status": "FAILED",
            "timestamp": datetime.now(timezone.utc),
            "message": f"Auditing failed: {str(e)}",
        }
        return {"agent_logs": [log]}
