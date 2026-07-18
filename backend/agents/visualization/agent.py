"""
Visualization Agent LangGraph Node.
Generates deterministic chart configurations and Tableau exports based on the Planner's analysis plan.
"""
import time
from datetime import datetime, timezone
from typing import Dict, Any

from backend.state.state import FinSightState, AgentLog
from backend.utils.logger import logger

from .schemas import VisualizationResult
from .chart_generator import ChartRegistry
from .tableau_exporter import export_to_tableau

def visualization_node(state: FinSightState) -> Dict[str, Any]:
    """Main execution logic for the Visualization Agent."""
    start_time = time.time()
    agent_name = "Visualization Agent"
    
    df = state.get("cleaning_results", {}).get("cleaned_dataframe")
    if df is None:
        df = state.get("dataset_info", {}).get("raw_dataframe")
        
    if df is None or df.empty:
        logger.error(f"{agent_name}: Empty dataframe.")
        return {"agent_logs": [{"agent_name": agent_name, "status": "FAILED", "timestamp": datetime.now(timezone.utc), "message": "Empty dataframe.", "provider_used": "Pandas", "llm_calls": 0, "estimated_tokens": 0, "estimated_cost": 0.0, "warnings": []}]}
        
    workflow_tracking = state.get("workflow_tracking", {})
    analysis_plan = workflow_tracking.get("analysis_plan", [])
    workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
    
    # Generate Charts using Strategy Registry (Planner-Aware)
    registry = ChartRegistry(workflow_id)
    charts, skipped_count = registry.generate_all(df, analysis_plan)
    
    result = VisualizationResult(
        charts=charts,
        tableau_export_path=""
    )
    
    # Export to Tableau Folder
    export_path = export_to_tableau(df, state, result, workflow_id)
    result.tableau_export_path = export_path
    
    rendering_time = time.time() - start_time
    
    log: AgentLog = {
        "agent_name": agent_name,
        "status": "COMPLETED",
        "timestamp": datetime.now(timezone.utc),
        "message": f"Generated {len(charts)} charts. Skipped {skipped_count}. Render time: {rendering_time:.2f}s. Export: {export_path}",
        "provider_used": "Deterministic Strategy Engine",
        "llm_calls": 0,
        "estimated_tokens": 0,
        "estimated_cost": 0.0,
        "warnings": []
    }
    
    return {
        "visualization": result.model_dump(),
        "workflow_tracking": {
            **workflow_tracking,
            "current_agent": agent_name,
            "completed_agents": workflow_tracking.get("completed_agents", []) + [agent_name],
            "execution_time": rendering_time
        },
        "agent_logs": [log]
    }
