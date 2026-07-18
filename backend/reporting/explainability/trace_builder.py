from backend.state.state import FinSightState
from backend.services.artifact_manager import ArtifactManager
from backend.utils.logger import logger

from .agent_summary import extract_agent_summaries
from .timeline_builder import build_workflow_timeline
from .trace_html_builder import generate_trace_html


def build_workflow_trace(state: FinSightState, workflow_id: str):
    """
    Orchestrates the Explainability Module.
    Generates agent traces, timelines, and the Trace HTML UI.
    """
    artifact_mgr = ArtifactManager(workflow_id)
    dataset_name = state.get("dataset_info", {}).get("filename", "Dataset")

    try:
        # 1. Agent Summaries
        agent_trace = extract_agent_summaries(state)
        artifact_mgr.save_json("logs", "agent_trace.json", agent_trace)

        # 2. Workflow Timeline
        timeline = build_workflow_timeline(state)
        artifact_mgr.save_json("logs", "workflow_timeline.json", timeline)

        # 3. Trace HTML UI
        trace_html = generate_trace_html(agent_trace, timeline, dataset_name)
        artifact_mgr.save_text("dashboard", "Trace.html", trace_html)

        logger.info(
            f"Explainability Module: Successfully generated traces for workflow {workflow_id}"
        )
    except Exception as e:
        logger.error(f"Explainability Module: Failed to generate trace: {e}")
