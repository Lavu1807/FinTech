from typing import Dict, Any
from backend.state.state import FinSightState


def build_workflow_timeline(state: FinSightState) -> Dict[str, Any]:
    """
    Parses agent_logs and execution_metadata to compute quantitative metrics
    and construct the execution timeline.
    """
    meta = state.get("execution_metadata", {})
    agent_logs = state.get("agent_logs", [])

    timeline = []
    agent_times = {}
    total_calls = 0
    total_tokens = 0
    total_cost = 0.0

    # 1. Generate Timeline
    for log in agent_logs:
        agent_name = log.get("agent_name", "Unknown Agent")
        status = log.get("status", "UNKNOWN")
        start_time = log.get("start_time")
        end_time = log.get("end_time")

        # Calculate duration if not present but timestamps exist
        duration = log.get("duration", 0.0)

        calls = log.get("llm_calls", 0)
        tokens = log.get("estimated_tokens", 0)
        cost = log.get("estimated_cost", 0.0)

        warnings = []
        if status == "FAILED" or "error" in log.get("message", "").lower():
            warnings.append(log.get("message"))

        timeline.append(
            {
                "agent": agent_name,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "status": status,
                "provider": log.get("provider_used", "N/A"),
                "llm_calls": calls,
                "token_usage": tokens,
                "estimated_cost": cost,
                "warnings": warnings,
                "message": log.get("message", ""),
            }
        )

        agent_times[agent_name] = agent_times.get(agent_name, 0.0) + duration
        total_calls += calls
        total_tokens += tokens
        total_cost += cost

    # 2. Compute Performance Metrics
    slowest_agent = None
    fastest_agent = None
    if agent_times:
        slowest_agent = max(agent_times.items(), key=lambda x: x[1])[0]
        fastest_agent = min(agent_times.items(), key=lambda x: x[1])[0]

    execution_graph = state.get("workflow_tracking", {}).get("execution_graph", [])
    if not execution_graph:
        execution_graph = (
            ["START"]
            + state.get("workflow_tracking", {}).get("completed_agents", [])
            + ["END"]
        )

    return {
        "execution_summary": {
            "total_execution_time": meta.get(
                "total_execution_time", sum(agent_times.values())
            ),
            "slowest_agent": slowest_agent,
            "fastest_agent": fastest_agent,
            "total_llm_calls": max(meta.get("total_llm_calls", 0), total_calls),
            "total_tokens": max(meta.get("total_tokens", 0), total_tokens),
            "total_estimated_cost": max(
                meta.get("estimated_llm_cost", 0.0), total_cost
            ),
        },
        "critical_path": execution_graph,
        "timeline": timeline,
        "per_agent_execution_time": agent_times,
    }
