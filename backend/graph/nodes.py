"""
LangGraph Node Wrappers for FinSight AI.
Handles exception interception and state mutations.
"""
from typing import Dict, Any
from backend.state.state import FinSightState

# Import all agents
from backend.agents.auditor.agent import auditor_node
from backend.agents.planner.planner_node import planner_node
from backend.agents.analytics.agent import analytics_node
from backend.agents.insights.agent import insight_node
from backend.agents.validation.agent import validation_node
from backend.agents.visualization.agent import visualization_node
from backend.agents.report.agent import report_node

from .hooks import before_node, after_node, on_error
from .runtime import with_retries

def _execute_node(state: FinSightState, node_func: callable, node_name: str, critical: bool = True) -> Dict[str, Any]:
    """Wraps agent execution with hooks to handle telemetry and failures safely."""
    start_time = before_node(node_name, state)
    try:
        result = node_func(state)
        return after_node(node_name, state, result, start_time)
    except Exception as e:
        return on_error(node_name, e, state, critical=critical)

def auditor_step(state: FinSightState) -> Dict[str, Any]:
    return _execute_node(state, auditor_node, "Data Auditor Agent", critical=True)

@with_retries(max_retries=3, base_delay=2.0)
def planner_step(state: FinSightState) -> Dict[str, Any]:
    return _execute_node(state, planner_node, "Planner Agent", critical=True)

def analytics_step(state: FinSightState) -> Dict[str, Any]:
    return _execute_node(state, analytics_node, "Analytics Agent", critical=True)

@with_retries(max_retries=3, base_delay=2.0)
def insights_step(state: FinSightState) -> Dict[str, Any]:
    return _execute_node(state, insight_node, "Insight Agent", critical=False)

def validation_step(state: FinSightState) -> Dict[str, Any]:
    return _execute_node(state, validation_node, "Validation Agent", critical=False)

def visualization_step(state: FinSightState) -> Dict[str, Any]:
    return _execute_node(state, visualization_node, "Visualization Agent", critical=False)

@with_retries(max_retries=3, base_delay=2.0)
def report_step(state: FinSightState) -> Dict[str, Any]:
    return _execute_node(state, report_node, "Report Generator Agent", critical=False)
