import os
from pathlib import Path

from backend.state.state import FinSightState
from backend.config.settings import settings
from backend.utils.logger import logger

from .manifest import generate_package_manifest
from .zip_exporter import export_to_zip

class PackageBuilder:
    """
    Orchestrates the Artifact Packaging System.
    Builds the complete ZIP package for a workflow execution in exports/packages/.
    """
    def __init__(self, workflow_id: str):
        self.workflow_id = str(Path(workflow_id).name)
        self.package_dir = Path(settings.EXPORTS_DIR) / "packages"
        self.package_dir.mkdir(parents=True, exist_ok=True)
        self.workflow_dir = settings.workflows_dir / self.workflow_id

    def build_package(self, state: FinSightState) -> str:
        """
        Gathers all artifacts, generates the manifest, and creates the final ZIP.
        Returns the absolute path to the generated ZIP file.
        """
        logger.info(f"PackageBuilder: Starting packaging process for {self.workflow_id}")
        
        # Gather currently generated files
        generated_files = []
        if self.workflow_dir.exists():
            for root, _, files in os.walk(self.workflow_dir):
                for file in files:
                    if file != "Results.zip":
                        rel = Path(root).relative_to(self.workflow_dir) / file
                        generated_files.append(str(rel).replace("\\", "/"))
        
        # 1. Generate new structured Manifest in the workflow dir before zipping
        manifest = generate_package_manifest(state, generated_files)
        manifest_path = self.workflow_dir / "package_manifest.json"
        
        # Write manifest if workflow dir exists
        if self.workflow_dir.exists():
            import json
            try:
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=4)
                if "package_manifest.json" not in generated_files:
                    generated_files.append("package_manifest.json")
            except Exception as e:
                logger.warning(f"PackageBuilder: Failed to write package_manifest.json: {e}")

        # 2. Export to ZIP
        zip_path = export_to_zip(self.workflow_id, self.package_dir)
        
        return str(zip_path)
