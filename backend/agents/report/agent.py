"""
Report Generator Agent LangGraph Node.
"""
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from backend.state.state import FinSightState
from backend.utils.logger import logger

from .schemas import ReportOutput
from .markdown_exporter import generate_markdown
from .html_exporter import generate_html
from .manifest import generate_manifest

def report_node(state: FinSightState) -> Dict[str, Any]:
    agent_name = "Report Generator Agent"
    time.time()
    
    filename = state.get("dataset_info", {}).get("filename", "unknown_dataset")
    base_name = filename.split('.')[0] if '.' in filename else filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
    from backend.services.artifact_manager import ArtifactManager
    artifact_mgr = ArtifactManager(workflow_id)
    
    md_name = f"{base_name}_report_{timestamp}.md"
    html_name = f"{base_name}_report_{timestamp}.html"
    pdf_name = f"{base_name}_report_{timestamp}.pdf"
    manifest_name = "report_manifest.json"
    
    try:
        exported_files = []
        # 1. Generate Markdown
        md_text = generate_markdown(state, filename)
        md_path = artifact_mgr.save_text("reports", md_name, md_text)
        exported_files.append(md_path)
            
        # 2. Generate HTML
        html_text = generate_html(md_text, state)
        html_path = artifact_mgr.save_text("reports", html_name, html_text)
        exported_files.append(html_path)
            
        # 3. Generate Executive PDF Report (ReportLab)
        from backend.reporting.pdf import export_pdf_report
        pdf_path = str(artifact_mgr.get_reports_dir() / pdf_name)
        final_pdf_path = export_pdf_report(state, pdf_path)
        success = bool(final_pdf_path)
        if success:
            exported_files.append(final_pdf_path)
            
        # 4. Generate Manifest
        manifest = generate_manifest(state, exported_files)
        manifest_path = artifact_mgr.save_json("reports", manifest_name, manifest)
        exported_files.append(manifest_path)
        
        # 5. Generate Standalone HTML Dashboard
        from backend.reporting.dashboard import export_html_dashboard
        downloads = {
            "PDF Report": f"../reports/{Path(final_pdf_path).name}" if final_pdf_path else None,
            "Markdown Report": f"../reports/{Path(md_path).name}" if md_path else None,
            "Analytics JSON": "../analytics/analytics.json" if (artifact_mgr.get_analytics_dir() / "analytics.json").exists() else None,
            "Validation JSON": "../validation/validation.json" if (artifact_mgr.get_validation_dir() / "validation.json").exists() else None,
            "Workflow Trace UI": "Trace.html"
        }
        dashboard_path = export_html_dashboard(state, downloads=downloads)
        if dashboard_path:
            exported_files.append(dashboard_path)
            
        # 6. Generate Explainability Trace
        from backend.reporting.explainability import build_workflow_trace
        build_workflow_trace(state, workflow_id)
        
        exec_summary = state.get("ai_insights", {}).get("executive_summary", "")
        if isinstance(exec_summary, dict):
            exec_summary = exec_summary.get("executive_summary", "")
            
        report_output = ReportOutput(
            executive_summary=exec_summary,
            markdown_report_path=md_path,
            pdf_report_path=final_pdf_path,
            html_report_path=html_path,
            dashboard_html_path=dashboard_path,
            report_manifest=manifest
        )
        
        log = {
            "agent_name": agent_name,
            "status": "COMPLETED",
            "timestamp": datetime.now(timezone.utc),
            "message": f"Generated Markdown/HTML. PDF Success: {success}",
            "provider_used": "Deterministic",
            "llm_calls": 0,
            "estimated_tokens": 0,
            "estimated_cost": 0.0,
            "warnings": [] if success else ["PDF generation skipped due to missing dependencies."]
        }
        
        workflow_tracking = state.get("workflow_tracking", {})
        
        return {
            "reports": report_output.model_dump(),
            "workflow_tracking": {
                **workflow_tracking,
                "current_agent": agent_name,
                "completed_agents": workflow_tracking.get("completed_agents", []) + [agent_name]
            },
            "agent_logs": [log]
        }
        
    except Exception as e:
        logger.error(f"{agent_name} critical failure: {str(e)}")
        log = {
            "agent_name": agent_name,
            "status": "FAILED",
            "timestamp": datetime.now(timezone.utc),
            "message": str(e),
            "provider_used": "Unknown",
            "llm_calls": 0,
            "estimated_tokens": 0,
            "estimated_cost": 0.0,
            "warnings": []
        }
        return {"agent_logs": [log]}
