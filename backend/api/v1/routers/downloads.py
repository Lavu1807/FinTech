from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.config.settings import settings

router = APIRouter(tags=["Downloads"])

def _get_file_response(workflow_id: str, subfolder: str, filename: str) -> FileResponse:
    # Sanitize workflow_id and filename to prevent path traversal
    safe_workflow_id = Path(workflow_id).name
    safe_filename = Path(filename).name
    
    # Check workflow-specific folder
    filepath = settings.workflows_dir / safe_workflow_id / subfolder / safe_filename
    
    # Path traversal validation
    exports_root = Path(settings.EXPORTS_DIR).resolve()
    if not filepath.resolve().is_relative_to(exports_root):
        raise HTTPException(status_code=403, detail="Invalid path request.")
        
    if not filepath.exists():
        # Fallback to global
        filepath = Path(settings.EXPORTS_DIR) / subfolder / safe_filename
        if not filepath.resolve().is_relative_to(exports_root):
            raise HTTPException(status_code=403, detail="Invalid path request.")
        
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found. Workflow may not have completed.")
    return FileResponse(path=filepath, filename=f"{safe_workflow_id}_{safe_filename}")

@router.get("/download/pdf/{workflow_id}")
async def download_pdf_report(workflow_id: str):
    """Downloads the generated PDF report."""
    return _get_file_response(workflow_id, "reports", "executive_report.pdf")

@router.get("/download/markdown/{workflow_id}")
async def download_markdown_report(workflow_id: str):
    """Downloads the generated Markdown report."""
    return _get_file_response(workflow_id, "reports", "executive_report.md")

@router.get("/download/analytics/{workflow_id}")
async def download_analytics(workflow_id: str):
    """Downloads the raw analytics JSON."""
    return _get_file_response(workflow_id, "analytics", "business_analytics.json")

@router.get("/download/validation/{workflow_id}")
async def download_validation(workflow_id: str):
    """Downloads the validation report JSON."""
    return _get_file_response(workflow_id, "validation", "validation_report.json")

@router.get("/download/dashboard/{workflow_id}")
async def download_dashboard(workflow_id: str):
    """Downloads the dashboard JSON."""
    return _get_file_response(workflow_id, "dashboard", "dashboard.json")

@router.get("/download/all/{workflow_id}")
async def download_zip_archive(workflow_id: str):
    """
    Packages all generated reports, charts, analytics, and dashboard JSONs
    for a specific workflow into a single ZIP archive and returns it.
    """
    try:
        from backend.reporting.package import PackageBuilder
        from backend.state.state import FinSightState
        
        # We need to construct or mock a FinSightState to pass to build_package if we don't have it in memory,
        # but since we are just packaging what's already on disk, we can pass a dummy state containing the workflow_id.
        dummy_state = FinSightState()
        dummy_state["execution_metadata"] = {"workflow_id": workflow_id}
        dummy_state["workflow_tracking"] = {"workflow_id": workflow_id}
        
        builder = PackageBuilder(workflow_id)
        zip_path = builder.build_package(dummy_state)
        
        return FileResponse(
            path=zip_path,
            filename=f"FinSight_Report_{workflow_id}.zip",
            media_type="application/zip"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ZIP archive: {e}")
