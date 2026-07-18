import os
import zipfile
from pathlib import Path
from backend.config.settings import settings
from backend.utils.logger import logger


def create_export_zip(workflow_id: str = None) -> Path:
    """
    Packages all generated exports into a single ZIP file.
    If workflow_id is provided, it packages the workflow-specific folder.
    Returns the path to the generated ZIP archive.
    """
    export_dir = Path(settings.EXPORTS_DIR)

    if workflow_id:
        safe_workflow_id = Path(workflow_id).name
        source_dir = settings.workflows_dir / safe_workflow_id
        if not source_dir.exists():
            source_dir = export_dir  # Fallback
        zip_path = export_dir / f"finsight_export_{safe_workflow_id}.zip"
    else:
        source_dir = export_dir
        zip_path = export_dir / "finsight_export.zip"

    # Folders to include in the archive
    target_folders = [
        "reports",
        "charts",
        "analytics",
        "dashboard",
        "validation",
        "insights",
    ]

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for folder_name in target_folders:
                folder_path = source_dir / folder_name
                if not folder_path.exists():
                    continue

                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = Path(root) / file
                        # Calculate path relative to the source directory
                        arcname = file_path.relative_to(source_dir)
                        zipf.write(file_path, arcname)

        logger.info(f"Successfully packaged exports to {zip_path}")
        return zip_path

    except Exception as e:
        logger.error(f"Failed to create export ZIP: {e}")
        raise
