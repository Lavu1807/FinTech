from fastapi import APIRouter
from backend.api.v1.routers import (
    health,
    upload,
    analysis,
    workflow,
    dashboard,
    analytics,
    insights,
    validation,
    reports,
    downloads,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(analysis.router)
api_router.include_router(workflow.router)
api_router.include_router(dashboard.router)
api_router.include_router(analytics.router)
api_router.include_router(insights.router)
api_router.include_router(validation.router)
api_router.include_router(reports.router)
api_router.include_router(downloads.router)
