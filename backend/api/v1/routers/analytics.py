from fastapi import APIRouter
from backend.api.v1.routers.dashboard import _load_workflow_json

router = APIRouter(tags=["Analytics"])

@router.get("/analytics/{workflow_id}")
async def get_analytics(workflow_id: str):
    """Retrieves the business analytics for a workflow."""
    return _load_workflow_json(workflow_id, "analytics", "business_analytics.json")
