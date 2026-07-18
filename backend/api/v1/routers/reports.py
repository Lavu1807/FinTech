from fastapi import APIRouter
from backend.api.v1.routers.dashboard import _load_workflow_json

router = APIRouter(tags=["Reports"])

@router.get("/reports/{workflow_id}")
async def get_reports(workflow_id: str):
    """Retrieves the generated report metadata for a workflow."""
    return _load_workflow_json(workflow_id, "reports", "report_manifest.json")
