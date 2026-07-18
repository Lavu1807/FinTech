"""
FinSight AI Workflow Setup.
Wires all nodes and conditional edges.
"""

from langgraph.graph import StateGraph
from backend.state.state import FinSightState

from .nodes import (
    auditor_step,
    planner_step,
    analytics_step,
    insights_step,
    validation_step,
    visualization_step,
    report_step,
)
from .edges import (
    NODE_AUDITOR,
    NODE_PLANNER,
    NODE_ANALYTICS,
    NODE_INSIGHTS,
    NODE_VALIDATION,
    NODE_VISUALIZATION,
    NODE_REPORT,
)
from .router import (
    route_after_auditor,
    route_after_planner,
    route_after_analytics,
    route_after_insights,
    route_after_validation,
    route_after_visualization,
    route_after_report,
)


def build_workflow() -> StateGraph:
    workflow = StateGraph(FinSightState)

    # Add Nodes
    workflow.add_node(NODE_AUDITOR, auditor_step)
    workflow.add_node(NODE_PLANNER, planner_step)
    workflow.add_node(NODE_ANALYTICS, analytics_step)
    workflow.add_node(NODE_INSIGHTS, insights_step)
    workflow.add_node(NODE_VALIDATION, validation_step)
    workflow.add_node(NODE_VISUALIZATION, visualization_step)
    workflow.add_node(NODE_REPORT, report_step)

    # Entry Point
    workflow.set_entry_point(NODE_AUDITOR)

    # Add Conditional Edges
    workflow.add_conditional_edges(NODE_AUDITOR, route_after_auditor)
    workflow.add_conditional_edges(NODE_PLANNER, route_after_planner)
    workflow.add_conditional_edges(NODE_ANALYTICS, route_after_analytics)
    workflow.add_conditional_edges(NODE_INSIGHTS, route_after_insights)
    workflow.add_conditional_edges(NODE_VALIDATION, route_after_validation)
    workflow.add_conditional_edges(NODE_VISUALIZATION, route_after_visualization)
    workflow.add_conditional_edges(NODE_REPORT, route_after_report)

    return workflow
