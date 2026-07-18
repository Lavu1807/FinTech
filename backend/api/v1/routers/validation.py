from fastapi import APIRouter
from backend.api.v1.routers.dashboard import _load_workflow_json

router = APIRouter(tags=["Validation"])


@router.get("/validation/{workflow_id}")
async def get_validation(workflow_id: str):
    """Retrieves the validation report for a workflow."""
    return _load_workflow_json(workflow_id, "validation", "validation_report.json")
