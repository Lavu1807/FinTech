"""
Conditional Routing Logic for FinSight AI.
"""
from backend.state.state import FinSightState
from .edges import END, NODE_PLANNER, NODE_ANALYTICS, NODE_INSIGHTS, NODE_VALIDATION, NODE_VISUALIZATION, NODE_REPORT

def route_after_auditor(state: FinSightState) -> str:
    if state.get("error_messages"):
        return END
    return NODE_PLANNER

def route_after_planner(state: FinSightState) -> str:
    if state.get("error_messages"):
        return END
    return NODE_ANALYTICS

def route_after_analytics(state: FinSightState) -> str:
    if state.get("error_messages"):
        return END
    # Skip insights if no analytical KPIs were generated
    kpis = state.get("business_analytics", {}).get("calculated_kpis", {})
    if not kpis:
        return NODE_VISUALIZATION
    return NODE_INSIGHTS

def route_after_insights(state: FinSightState) -> str:
    if state.get("error_messages"):
        return END
    return NODE_VALIDATION

def route_after_validation(state: FinSightState) -> str:
    if state.get("error_messages"):
        return END
    return NODE_VISUALIZATION

def route_after_visualization(state: FinSightState) -> str:
    if state.get("error_messages"):
        return END
    return NODE_REPORT

def route_after_report(state: FinSightState) -> str:
    return END
