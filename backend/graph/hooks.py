"""
Centralized Execution Hooks for LangGraph nodes.
Provides uniform logging and telemetry interceptors.
"""

from datetime import datetime, timezone
import time
from typing import Dict, Any
from backend.utils.logger import logger
from backend.state.state import FinSightState
from backend.utils.telemetry import ExecutionTelemetry


def validate_dependencies(node_name: str, state: FinSightState):
    """Pre-flight checks to ensure the state has required data before execution."""
    requirements = {
        "Planner Agent": ["dataset_profile"],
        "Analytics Agent": ["cleaning_results"],
        "Insight Agent": ["business_analytics"],
        "Validation Agent": ["ai_insights"],
        "Visualization Agent": ["business_analytics"],
        "Report Generator Agent": [
            "dataset_profile",
            "business_analytics",
            "ai_insights",
        ],
    }

    if node_name in requirements:
        for req in requirements[node_name]:
            if not state.get(req):
                raise ValueError(
                    f"Dependency missing: {node_name} requires {req} in state."
                )


def before_node(node_name: str, state: FinSightState) -> float:
    """Executes before a node runs. Validates state and returns the start timestamp."""
    logger.info(f"--- STARTING {node_name} ---")
    validate_dependencies(node_name, state)
    return time.time()


def after_node(
    node_name: str, state: FinSightState, result: Dict[str, Any], start_time: float
) -> Dict[str, Any]:
    """Executes after a node successfully completes."""
    duration = time.time() - start_time
    logger.info(f"--- FINISHED {node_name} in {duration:.2f}s ---")

    # Propagate failures if the agent explicitly logged a failure internally
    if result and "agent_logs" in result:
        for log in result["agent_logs"]:
            if log.get("status") == "FAILED":
                return on_error(
                    node_name,
                    Exception(log.get("message", "Unknown error")),
                    state,
                    critical=True,
                )

    # Capture Timeline Event
    timeline_event = {
        "agent_name": node_name,
        "start_time": datetime.fromtimestamp(start_time).isoformat(),
        "finish_time": datetime.now(timezone.utc).isoformat(),
        "duration": duration,
        "status": "COMPLETED",
        "provider_used": "Unknown",
        "llm_calls": 0,
        "tokens_used": 0,
        "estimated_cost": 0.0,
        "warnings": [],
    }

    # Enrich with agent logs if available
    if result and "agent_logs" in result and result["agent_logs"]:
        latest_log = result["agent_logs"][-1]
        timeline_event["provider_used"] = latest_log.get("provider_used", "Unknown")
        timeline_event["llm_calls"] = latest_log.get("llm_calls", 0)
        timeline_event["tokens_used"] = latest_log.get("estimated_tokens", 0)
        timeline_event["estimated_cost"] = latest_log.get("estimated_cost", 0.0)
        timeline_event["warnings"] = latest_log.get("warnings", [])

    execution_metadata = state.get("execution_metadata", {})
    existing_timeline = execution_metadata.get("timeline", [])

    # Important: if the agent updated execution_metadata in its result, we must merge
    result_exec_meta = result.get("execution_metadata", {})
    merged_exec_meta = {**execution_metadata, **result_exec_meta}
    merged_exec_meta["timeline"] = existing_timeline + [timeline_event]

    result["execution_metadata"] = merged_exec_meta

    return result


def on_error(
    node_name: str, error: Exception, state: FinSightState, critical: bool = True
) -> Dict[str, Any]:
    """Intercepts node errors and maps them to workflow failures."""
    err_msg = f"{node_name} failed: {str(error)}"
    logger.error(err_msg)

    ExecutionTelemetry.generate_failure_report(state, error, node_name)

    if critical:
        return {"error_messages": [err_msg]}
    else:
        # Non-critical failures just log and pass an empty dict to not break state
        return {}
