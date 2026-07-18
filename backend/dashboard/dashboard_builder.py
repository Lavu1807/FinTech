from typing import List
from backend.state.state import FinSightState
from backend.utils.logger import logger

from .schemas import WorkflowDashboard, AgentExecution
from .timeline import build_timeline
from .summary import build_summary, build_metrics

def _extract_agents(state: FinSightState) -> List[AgentExecution]:
    agents = []
    agent_logs = state.get("agent_logs", [])
    
    start_time = state.get("execution_metadata", {}).get("execution_start")
    last_timestamp = start_time
    
    for log in agent_logs:
        timestamp = log.get("timestamp")
        
        # Calculate duration based on previous timestamp
        duration = 0.0
        if last_timestamp and timestamp:
            duration = (timestamp - last_timestamp).total_seconds()
            
        agents.append(AgentExecution(
            agent_name=log.get("agent_name", "Unknown"),
            status=log.get("status", "COMPLETED"),
            start_time=last_timestamp or timestamp,
            end_time=timestamp,
            duration=max(0.0, duration),
            provider_used=log.get("provider_used"),
            llm_calls=log.get("llm_calls", 0),
            estimated_tokens=log.get("estimated_tokens", 0),
            estimated_cost=log.get("estimated_cost", 0.0),
            warnings=log.get("warnings", []),
            summary_message=log.get("message", "")
        ))
        
        last_timestamp = timestamp
        
    return agents

def get_dashboard(state: FinSightState) -> WorkflowDashboard:
    """Builds the in-memory WorkflowDashboard Pydantic model."""
    agents = _extract_agents(state)
    summary = build_summary(state)
    timeline = build_timeline(state)
    metrics = build_metrics(state, agents)
    
    # Extract execution graph explicitly requested
    workflow_tracking = state.get("workflow_tracking", {})
    execution_graph = workflow_tracking.get("completed_agents", [])
    
    return WorkflowDashboard(
        summary=summary,
        timeline=timeline,
        metrics=metrics,
        agents=agents,
        execution_graph=execution_graph
    )

def build_dashboard(state: FinSightState) -> None:
    """
    Builds the dashboard and writes exports to backend/exports/dashboard/ safely.
    Will append a warning if export fails, but will not crash the workflow.
    """
    try:
        dashboard = get_dashboard(state)
        
        workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
        from backend.services.artifact_manager import ArtifactManager
        artifact_mgr = ArtifactManager(workflow_id)
        
        artifact_mgr.save_json("dashboard", "dashboard.json", dashboard.model_dump())
        artifact_mgr.save_json("dashboard", "timeline.json", [t.model_dump() for t in dashboard.timeline])
        artifact_mgr.save_json("dashboard", "execution_summary.json", dashboard.summary.model_dump())
        artifact_mgr.save_json("dashboard", "execution_metrics.json", dashboard.metrics.model_dump())
        
        logger.info(f"Dashboard metadata successfully exported to {artifact_mgr.get_dashboard_dir()}")
        
    except Exception as e:
        logger.warning(f"Failed to export execution dashboard: {e}")
        state.setdefault("error_messages", []).append(f"Dashboard export failed: {e}")
