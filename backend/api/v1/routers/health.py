import os
from pathlib import Path
from fastapi import APIRouter, status
from backend.config.settings import settings
from backend.api.v1.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["System"])

def _check_export_dir() -> bool:
    try:
        export_dir = Path(settings.EXPORTS_DIR)
        export_dir.mkdir(parents=True, exist_ok=True)
        return os.access(export_dir, os.W_OK)
    except Exception:
        return False

def _check_llm() -> bool:
    # In a real scenario, we might make a fast ping to the LLM
    return bool(settings.GEMINI_API_KEY)

@router.get("", response_model=HealthResponse)
def health_check():
    """Returns the comprehensive health status of the platform."""
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        llm_available=_check_llm(),
        exports_dir_writable=_check_export_dir()
    )

@router.get("/live", status_code=status.HTTP_200_OK)
def liveness_probe():
    """Simple ping for load balancers."""
    return {"status": "alive"}

@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_probe():
    """Check if application dependencies are satisfied."""
    if not _check_export_dir():
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Exports directory not writable")
    return {"status": "ready"}
