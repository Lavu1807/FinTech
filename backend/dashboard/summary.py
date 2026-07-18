from typing import List
from backend.state.state import FinSightState
from .schemas import WorkflowSummary, ExecutionMetrics, AgentExecution


def build_summary(state: FinSightState) -> WorkflowSummary:
    execution_metadata = state.get("execution_metadata", {})
    workflow_tracking = state.get("workflow_tracking", {})
    dataset_info = state.get("dataset_info", {})
    agent_logs = state.get("agent_logs", [])
    error_messages = state.get("error_messages", [])

    # Calculate failed agents
    failed_agents = [
        log.get("agent_name", "") for log in agent_logs if log.get("status") == "FAILED"
    ]
    completed_agents = workflow_tracking.get("completed_agents", [])

    # Calculate total warnings
    warnings_count = sum(len(log.get("warnings", [])) for log in agent_logs)

    status = "COMPLETED"
    if error_messages or failed_agents:
        status = "FAILED"
    elif warnings_count > 0:
        status = "COMPLETED_WITH_WARNINGS"

    return WorkflowSummary(
        workflow_status=status,
        execution_time=execution_metadata.get("total_execution_time", 0.0),
        total_cost=execution_metadata.get("estimated_llm_cost", 0.0),
        total_tokens=execution_metadata.get("total_tokens", 0),
        total_llm_calls=execution_metadata.get("total_llm_calls", 0),
        dataset_name=dataset_info.get("filename", "Unknown"),
        dataset_type=dataset_info.get("dataset_category", "Unknown"),
        business_domain=dataset_info.get("business_domain", "Unknown"),
        planner_confidence=workflow_tracking.get("planner_confidence", 0.0),
        completed_agents=completed_agents,
        failed_agents=failed_agents,
        warnings_count=warnings_count,
    )


def build_metrics(
    state: FinSightState, agent_executions: List[AgentExecution]
) -> ExecutionMetrics:
    execution_metadata = state.get("execution_metadata", {})

    if not agent_executions:
        return ExecutionMetrics(
            total_runtime=0.0,
            average_agent_runtime=0.0,
            most_expensive_agent=None,
            slowest_agent=None,
            fastest_agent=None,
            total_estimated_cost=0.0,
            total_tokens=0,
            average_tokens_per_agent=0.0,
        )

    total_runtime = sum(a.duration for a in agent_executions)
    average_agent_runtime = (
        total_runtime / len(agent_executions) if agent_executions else 0.0
    )

    slowest_agent = max(agent_executions, key=lambda a: a.duration)
    fastest_agent = min(agent_executions, key=lambda a: a.duration)

    agents_with_cost = [a for a in agent_executions if a.estimated_cost > 0]
    most_expensive = (
        max(agents_with_cost, key=lambda a: a.estimated_cost)
        if agents_with_cost
        else None
    )

    total_tokens = sum(a.estimated_tokens for a in agent_executions)
    average_tokens_per_agent = (
        total_tokens / len(agent_executions) if agent_executions else 0.0
    )

    return ExecutionMetrics(
        total_runtime=total_runtime,
        average_agent_runtime=average_agent_runtime,
        most_expensive_agent=most_expensive.agent_name if most_expensive else None,
        slowest_agent=slowest_agent.agent_name,
        fastest_agent=fastest_agent.agent_name,
        total_estimated_cost=execution_metadata.get("estimated_llm_cost", 0.0),
        total_tokens=total_tokens,
        average_tokens_per_agent=average_tokens_per_agent,
    )
