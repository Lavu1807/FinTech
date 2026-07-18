from fastapi import APIRouter
from backend.api.v1.routers.dashboard import _load_workflow_json

router = APIRouter(tags=["Insights"])

@router.get("/insights/{workflow_id}")
async def get_insights(workflow_id: str):
    """Retrieves the AI insights for a workflow."""
    return _load_workflow_json(workflow_id, "insights", "ai_insights.json")
