"""
Manifest generator for the Artifact Packaging System.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.state.state import FinSightState


def generate_package_manifest(state: FinSightState, generated_files: List[str]) -> Dict[str, Any]:
    """Generates the comprehensive manifest.json for the final package."""
    meta = state.get("execution_metadata", {})
    workflow_tracking = state.get("workflow_tracking", {})
    dataset_info = state.get("dataset_info", {})
    
    agent_logs = state.get("agent_logs", [])
    
    # Calculate totals from agent logs if meta is incomplete
    total_tokens = sum([log.get("estimated_tokens", 0) for log in agent_logs])
    total_cost = sum([log.get("estimated_cost", 0.0) for log in agent_logs])
    
    # Provider is usually extracted from insights or planner
    providers = list(set([log.get("provider_used", "Unknown") for log in agent_logs if log.get("provider_used")]))
    primary_provider = providers[0] if providers else "Unknown"

    return {
        "workflow_id": workflow_tracking.get("workflow_id", "unknown"),
        "dataset_name": dataset_info.get("filename", "unknown"),
        "generation_time": datetime.now(timezone.utc).isoformat(),
        "execution_time": meta.get("total_execution_time", 0.0),
        "LLM_provider": primary_provider,
        "total_tokens": max(meta.get("total_tokens", 0), total_tokens),
        "estimated_cost": max(meta.get("estimated_llm_cost", 0.0), total_cost),
        "agent_execution_order": workflow_tracking.get("completed_agents", []),
        "generated_files": generated_files
    }
