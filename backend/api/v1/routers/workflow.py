from fastapi import APIRouter, HTTPException
from backend.api.v1.schemas import WorkflowStatusResponse
from backend.api.v1.routers.analysis import _WORKFLOW_STATUS

router = APIRouter(tags=["Workflow"])

@router.get("/workflow/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_status(workflow_id: str):
    """Retrieves the current execution status of a workflow."""
    status_data = _WORKFLOW_STATUS.get(workflow_id)
    if not status_data:
        raise HTTPException(status_code=404, detail=f"Workflow ID {workflow_id} not found")
        
    final_state = status_data.get("final_state", {})
    workflow_tracking = final_state.get("workflow_tracking", {})
    
    return WorkflowStatusResponse(
        workflow_id=workflow_id,
        status=status_data.get("status", "UNKNOWN"),
        current_agent=workflow_tracking.get("current_agent", "N/A") if status_data.get("status") != "COMPLETED" else "Done",
        completed_agents=workflow_tracking.get("completed_agents", []),
        remaining_agents=[], # Simplified for now
        runtime=final_state.get("execution_metadata", {}).get("total_execution_time", 0.0),
        progress_percentage=status_data.get("progress", 0.0)
    )
