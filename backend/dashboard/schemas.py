from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class TimelineEvent(BaseModel):
    timestamp: datetime
    event_name: str


class AgentExecution(BaseModel):
    agent_name: str
    status: str
    start_time: datetime
    end_time: datetime
    duration: float
    provider_used: Optional[str] = None
    llm_calls: int
    estimated_tokens: int
    estimated_cost: float
    warnings: List[str]
    summary_message: str


class ExecutionMetrics(BaseModel):
    total_runtime: float
    average_agent_runtime: float
    most_expensive_agent: Optional[str] = None
    slowest_agent: Optional[str] = None
    fastest_agent: Optional[str] = None
    total_estimated_cost: float
    total_tokens: int
    average_tokens_per_agent: float


class WorkflowSummary(BaseModel):
    workflow_status: str
    execution_time: float
    total_cost: float
    total_tokens: int
    total_llm_calls: int
    dataset_name: str
    dataset_type: str
    business_domain: str
    planner_confidence: float
    completed_agents: List[str]
    failed_agents: List[str]
    warnings_count: int


class WorkflowDashboard(BaseModel):
    summary: WorkflowSummary
    timeline: List[TimelineEvent]
    metrics: ExecutionMetrics
    agents: List[AgentExecution]
    execution_graph: List[str]
