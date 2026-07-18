import os
import zipfile
from pathlib import Path

from backend.config.settings import settings
from backend.utils.logger import logger

def export_to_zip(workflow_id: str, package_dir: Path) -> Path:
    """
    Creates a ZIP archive for a specific workflow, preserving directory structure.
    Skips missing files gracefully and never fails on missing artifacts.
    """
    safe_workflow_id = Path(workflow_id).name
    source_dir = settings.workflows_dir / safe_workflow_id
    
    # Ensure package dir exists
    package_dir.mkdir(parents=True, exist_ok=True)
    zip_path = package_dir / f"FinSight_Report_{safe_workflow_id}.zip"
    
    target_folders = ["analytics", "validation", "charts", "dashboard", "reports", "insights"]
    packaged_files = []
    
    if not source_dir.exists():
        logger.warning(f"ZipExporter: Source directory {source_dir} does not exist.")
        # Create empty zip to not break the pipeline
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            pass
        return zip_path
        
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Package subfolders
            for folder_name in target_folders:
                folder_path = source_dir / folder_name
                if not folder_path.exists():
                    logger.info(f"ZipExporter: Skipping missing folder '{folder_name}'.")
                    continue
                    
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = Path(root) / file
                        if not file_path.exists():
                            logger.warning(f"ZipExporter: File {file_path} vanished, skipping.")
                            continue
                            
                        # Keep relative paths clean in the ZIP
                        arcname = file_path.relative_to(source_dir)
                        zipf.write(file_path, arcname)
                        packaged_files.append(str(arcname))
            
            # Package root-level files in the source dir (like manifest.json if any)
            for item in source_dir.iterdir():
                if item.is_file() and item.name != "Results.zip": # Don't package old zips
                    arcname = item.relative_to(source_dir)
                    zipf.write(item, arcname)
                    packaged_files.append(str(arcname))
                    
        logger.info(f"ZipExporter successfully packaged {len(packaged_files)} files to {zip_path}")
        return zip_path
        
    except Exception as e:
        logger.error(f"ZipExporter encountered an error while packaging: {e}")
        # Return path anyway if it exists, or raise? Requirement says "Never fail if one artifact is unavailable"
        if zip_path.exists():
            return zip_path
        raise
