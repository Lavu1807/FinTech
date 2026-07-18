import uuid
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks
from backend.config.settings import settings
from backend.api.v1.schemas import AnalyzeRequest, AnalyzeResponse
from backend.graph.workflow_runner import run_workflow
from backend.api.exceptions import DatasetValidationError
from backend.utils.logger import logger

router = APIRouter(tags=["Analysis"])

# Global dictionary to track workflow status for the mock async implementation
# In a real enterprise app, this would be Redis or a Database
_WORKFLOW_STATUS = {}

def _execute_workflow_task(workflow_id: str, session_id: str, file_path: Path, filename: str):
    """Background task to run the LangGraph workflow."""
    try:
        df = pd.read_csv(file_path)
        _WORKFLOW_STATUS[workflow_id] = {"status": "RUNNING", "progress": 10.0, "current_agent": "Auditor"}
        
        # Run the actual LangGraph orchestration
        final_state = run_workflow(df, filename=filename, session_id=session_id, workflow_id=workflow_id)
        
        # Update status on completion
        _WORKFLOW_STATUS[workflow_id] = {
            "status": final_state.get("execution_metadata", {}).get("workflow_status", "COMPLETED"),
            "progress": 100.0,
            "final_state": final_state
        }
    except Exception as e:
        logger.exception(f"Workflow {workflow_id} failed: {e}")
        _WORKFLOW_STATUS[workflow_id] = {"status": "FAILED", "error": str(e), "progress": 0.0}

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_dataset(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Starts the LangGraph multi-agent analysis on an uploaded dataset."""
    safe_filename = Path(request.filename).name
    file_path = settings.uploads_dir / safe_filename
    
    if not file_path.exists():
        raise DatasetValidationError(f"Dataset {safe_filename} not found. Please upload first.")
        
    workflow_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    _WORKFLOW_STATUS[workflow_id] = {"status": "PENDING", "progress": 0.0}
    
    # Dispatch to background task
    background_tasks.add_task(_execute_workflow_task, workflow_id, session_id, file_path, request.filename)
    
    logger.info(f"Started analysis for {request.filename} with workflow_id {workflow_id}")
    
    return AnalyzeResponse(
        workflow_id=workflow_id,
        session_id=session_id,
        status="PENDING",
        estimated_runtime=45.0  # Estimated 45 seconds for a typical run
    )
