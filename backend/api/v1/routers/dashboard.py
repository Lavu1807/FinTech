import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.config.settings import settings
from backend.dashboard.schemas import WorkflowDashboard

router = APIRouter(tags=["Dashboard"])


def _load_workflow_json(workflow_id: str, subfolder: str, filename: str) -> dict:
    # First check if there's a workflow-specific archive folder
    filepath = (
        Path(settings.EXPORTS_DIR) / "workflows" / workflow_id / subfolder / filename
    )

    # Fallback to the global directory if it hasn't been archived yet
    if not filepath.exists():
        filepath = Path(settings.EXPORTS_DIR) / subfolder / filename

    if not filepath.exists():
        raise HTTPException(
            status_code=404, detail=f"{filename} not found for workflow {workflow_id}"
        )
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read {filename}: {e}")


@router.get("/dashboard/{workflow_id}", response_model=WorkflowDashboard)
async def get_dashboard(workflow_id: str):
    """Retrieves the comprehensive execution dashboard for a workflow."""
    return _load_workflow_json(workflow_id, "dashboard", "dashboard.json")
