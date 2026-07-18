"""
Main entrypoint for the FinSight AI Multi-Agent Workflow.
"""

from typing import Dict, Any
from datetime import datetime, timezone
import pandas as pd
import uuid

from backend.state.state import FinSightState
from backend.graph.workflow_executor import build_workflow
from backend.utils.telemetry import ExecutionTelemetry


def run_workflow(
    uploaded_dataframe: pd.DataFrame,
    filename: str = "dataset.csv",
    session_id: str = None,
    workflow_id: str = None,
) -> Dict[str, Any]:
    """
    Executes the entire LangGraph pipeline deterministically.

    This acts as the primary entrypoint for the FinSight AI multi-agent system.
    It takes a raw Pandas DataFrame and initializes a robust `FinSightState`
    TypedDict, which acts as the shared memory for all agents (Auditor, Planner,
    Analytics, Insight, Validation, Visualization, Report).

    Args:
        uploaded_dataframe (pd.DataFrame): The raw dataset uploaded by the user.
        filename (str): The name of the file for telemetry and display.
        session_id (str, optional): A unique ID correlating frontend requests.
        workflow_id (str, optional): A unique ID for this specific execution.

    Returns:
        Dict[str, Any]: The final populated FinSightState after all graph nodes complete.
    """
    workflow = build_workflow()

    session_id = session_id or str(uuid.uuid4())
    workflow_id = workflow_id or str(uuid.uuid4())

    # Initialize FinSightState
    initial_state: FinSightState = {
        "execution_metadata": {
            "workflow_id": workflow_id,
            "execution_start": datetime.now(timezone.utc),
            "execution_end": None,
            "total_execution_time": 0.0,
            "total_llm_calls": 0,
            "provider": "Multiple",
            "dataset_hash": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "latency": 0.0,
            "request_id": "",
            "estimated_llm_cost": 0.0,
            "estimated_runtime": 0.0,
            "prompt_version": "v3.0",
            "prompt_hash": "",
        },
        "session_info": {
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc),
            "workflow_stage": "STARTED",
            "requires_human_approval": False,
        },
        "dataset_info": {
            "filename": filename,
            "file_type": "csv",
            "dataset_category": "Unknown",
            "business_domain": "Unknown",
            "raw_dataframe": uploaded_dataframe,
        },
        "dataset_profile": {},
        "quality_metrics": {},
        "dataset_risks": [],
        "cleaning_results": {},
        "business_analytics": {},
        "visualization": {},
        "ai_insights": {},
        "validation": {},
        "reports": {},
        "chat_history": [],
        "workflow_tracking": {
            "analysis_plan": [],
            "planner_reasoning": [],
            "required_agents": [],
            "planner_confidence": 0.0,
            "completed_agents": [],
            "current_agent": "Initialization",
            "next_agent": "Auditor Agent",
            "execution_time": 0.0,
            "requires_manual_review": False,
            "dataset_complexity": "Unknown",
            "execution_graph": [],
        },
        "error_messages": [],
        "agent_logs": [],
    }

    config = {"configurable": {"thread_id": session_id}}

    # Run the graph
    final_state = workflow.invoke(initial_state, config=config)

    # Update final telemetry
    if "execution_metadata" in final_state:
        end_time = datetime.now(timezone.utc)
        start_time = final_state["execution_metadata"]["execution_start"]
        final_state["execution_metadata"]["execution_end"] = end_time
        final_state["execution_metadata"]["total_execution_time"] = (
            end_time - start_time
        ).total_seconds()

    # Generate Execution Telemetry
    ExecutionTelemetry.generate_workflow_exports(final_state)

    # Generate Dashboard Exports
    from backend.dashboard.dashboard_builder import build_dashboard

    build_dashboard(final_state)

    # Generate manifest via Artifact Manager (Deprecated packaging)
    from backend.services.artifact_manager import ArtifactManager

    artifact_mgr = ArtifactManager(workflow_id)
    artifact_mgr.generate_manifest(final_state)

    # Generate package using the new Packaging System
    from backend.reporting.package import PackageBuilder

    pkg_builder = PackageBuilder(workflow_id)
    pkg_builder.build_package(final_state)

    return final_state
