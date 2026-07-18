import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Union

from backend.config.settings import settings
from backend.utils.logger import logger

class ArtifactManager:
    """
    Centralized manager for all workflow artifacts.
    Ensures every workflow execution has its own isolated export directory
    and handles file saving directly into this structure.
    """
    def __init__(self, workflow_id: str):
        self.workflow_id = str(Path(workflow_id).name)  # Sanitize against path traversal
        self.base_dir = settings.workflows_dir / self.workflow_id
        
        # Define standardized subdirectories
        self.subdirs = {
            "reports": self.base_dir / "reports",
            "dashboard": self.base_dir / "dashboard",
            "charts": self.base_dir / "charts",
            "analytics": self.base_dir / "analytics",
            "insights": self.base_dir / "insights",
            "validation": self.base_dir / "validation",
            "logs": self.base_dir / "logs",
            "tableau": self.base_dir / "tableau",
            "profiling": self.base_dir / "profiling"
        }
        
        self._create_structure()

    def _create_structure(self):
        """Creates the workflow base directory and all subdirectories."""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            for d in self.subdirs.values():
                d.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create artifact structure for {self.workflow_id}: {e}")

    # --- Directory Getters ---
    def get_workflow_dir(self) -> Path:
        return self.base_dir
        
    def get_reports_dir(self) -> Path:
        return self.subdirs["reports"]
        
    def get_dashboard_dir(self) -> Path:
        return self.subdirs["dashboard"]
        
    def get_charts_dir(self) -> Path:
        return self.subdirs["charts"]
        
    def get_analytics_dir(self) -> Path:
        return self.subdirs["analytics"]
        
    def get_insights_dir(self) -> Path:
        return self.subdirs["insights"]
        
    def get_validation_dir(self) -> Path:
        return self.subdirs["validation"]
        
    def get_tableau_dir(self) -> Path:
        return self.subdirs["tableau"]
        
    def get_logs_dir(self) -> Path:
        return self.subdirs["logs"]
        
    def get_profiling_dir(self) -> Path:
        return self.subdirs["profiling"]

    # --- File Savers ---
    def _resolve_dir(self, subdir: Union[str, Path]) -> Path:
        """Resolves string subdir names ('charts') to actual Path objects, or returns the Path if provided."""
        if isinstance(subdir, str):
            if subdir in self.subdirs:
                return self.subdirs[subdir]
            # Fallback for unknown subdirs, create them within base_dir
            new_dir = self.base_dir / subdir
            new_dir.mkdir(parents=True, exist_ok=True)
            return new_dir
        return subdir

    def save_json(self, subdir: Union[str, Path], filename: str, data: Union[dict, list]) -> str:
        """Saves a JSON file and returns its absolute path."""
        target_dir = self._resolve_dir(subdir)
        filepath = target_dir / filename
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, default=str)
            return str(filepath)
        except Exception as e:
            logger.error(f"ArtifactManager failed to save JSON {filename}: {e}")
            return ""

    def save_text(self, subdir: Union[str, Path], filename: str, text: str) -> str:
        """Saves a text file and returns its absolute path."""
        target_dir = self._resolve_dir(subdir)
        filepath = target_dir / filename
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            return str(filepath)
        except Exception as e:
            logger.error(f"ArtifactManager failed to save text {filename}: {e}")
            return ""

    def save_binary(self, subdir: Union[str, Path], filename: str, content: bytes) -> str:
        """Saves a binary file (e.g. PNG, PDF) and returns its absolute path."""
        target_dir = self._resolve_dir(subdir)
        filepath = target_dir / filename
        try:
            with open(filepath, "wb") as f:
                f.write(content)
            return str(filepath)
        except Exception as e:
            logger.error(f"ArtifactManager failed to save binary {filename}: {e}")
            return ""
            
    # --- Generators ---
    def generate_manifest(self, state: Dict[str, Any]) -> str:
        """Generates the main manifest.json for this workflow."""
        dataset_name = state.get("dataset_info", {}).get("filename", "unknown")
        meta = state.get("execution_metadata", {})
        
        # Build relative paths map
        generated_files = []
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file != "manifest.json" and file != "README.txt":
                    rel_path = Path(root).relative_to(self.base_dir) / file
                    generated_files.append(str(rel_path).replace("\\", "/"))
                    
        manifest = {
            "workflow_id": self.workflow_id,
            "dataset_name": dataset_name,
            "creation_timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_metadata": {
                "total_execution_time": meta.get("total_execution_time", 0.0),
                "total_llm_calls": meta.get("total_llm_calls", 0),
                "estimated_llm_cost": meta.get("estimated_llm_cost", 0.0),
                "prompt_version": meta.get("prompt_version", "")
            },
            "generated_artifacts": generated_files
        }
        
        filepath = self.save_json(self.base_dir, "manifest.json", manifest)
        self.generate_readme() # Also trigger README generation
        logger.info(f"ArtifactManager successfully built workflow bundle at {self.base_dir}")
        return filepath
        
    def generate_readme(self) -> str:
        """Generates a README.txt explaining the folder contents."""
        readme = f'''FinSight AI - Workflow Artifacts
Workflow ID: {self.workflow_id}
Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}

Welcome to the generated artifact bundle for your dataset analysis!

=== HOW TO START ===
We highly recommend you open `dashboard/Dashboard.html` in your web browser first.
It contains a fully interactive, standalone summary of all insights, charts, and data quality metrics.

Alternatively, you can open `reports/Executive_Report_<timestamp>.pdf` for a professional consulting-grade PDF document.

=== DIRECTORY STRUCTURE ===
- /analytics : Raw JSON data for calculated KPIs, trends, and statistics.
- /charts    : High-resolution PNG visualizations generated from your data.
- /dashboard : Standalone interactive HTML dashboard.
- /insights  : JSON payloads containing AI-generated findings, risks, and recommendations.
- /logs      : Detailed execution metadata and LLM performance telemetry.
- /profiling : Initial data audit and quality reports.
- /reports   : Formatted PDF, HTML, and Markdown executive summaries.
- /tableau   : Ready-to-import CSVs and JSON layout manifests for Tableau or PowerBI.
- /validation: Hallucination and consistency checks from the Validation Agent.

For technical details, please refer to the `manifest.json` in this root directory.
'''
        return self.save_text(self.base_dir, "README.txt", readme)

    def bundle_results(self) -> str:
        """Zips the entire workflow directory into Results.zip and returns the path."""
        import shutil
        try:
            temp_zip = shutil.make_archive(
                str(self.base_dir / "Results"), 
                'zip', 
                root_dir=str(self.base_dir)
            )
            logger.info(f"Successfully bundled artifacts to {temp_zip}")
            return temp_zip
        except Exception as e:
            logger.error(f"Failed to bundle artifacts for {self.workflow_id}: {e}")
            return ""
