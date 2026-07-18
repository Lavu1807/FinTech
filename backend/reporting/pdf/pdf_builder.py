from datetime import datetime, timezone
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4

from backend.state.state import FinSightState
from backend.utils.logger import logger

from .pdf_sections import (
    build_cover_page,
    build_executive_summary,
    build_dataset_overview,
    build_data_quality,
    build_kpi_analysis,
    build_insights_and_risks,
    build_validation_summary,
    build_appendix,
)
from .charts import build_charts_section


def _on_page(canvas, doc):
    """Callback to draw header/footer on each page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawString(inch, 0.75 * inch, "FinSight AI — Confidential")
    canvas.drawRightString(A4[0] - inch, 0.75 * inch, f"Page {doc.page}")
    canvas.restoreState()


# For margins
from reportlab.lib.units import inch  # noqa: E402


def export_pdf_report(state: FinSightState, output_path: str = None) -> str:
    """Orchestrates building the PDF using ReportLab."""
    try:
        # Determine Path
        if not output_path:
            workflow_id = state.get("execution_metadata", {}).get(
                "workflow_id", "unknown"
            )
            from backend.services.artifact_manager import ArtifactManager

            artifact_mgr = ArtifactManager(workflow_id)
            export_dir = artifact_mgr.get_reports_dir()

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = str(export_dir / f"Executive_Report_{timestamp}.pdf")

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Build Story
        story = []
        dataset_name = state.get("dataset_info", {}).get("filename", "Dataset")
        workflow_id = state.get("execution_metadata", {}).get("workflow_id", "Unknown")
        date_str = datetime.now(timezone.utc).strftime("%d %B %Y")

        story.extend(build_cover_page(dataset_name, workflow_id, date_str))
        story.extend(build_executive_summary(state))
        story.extend(build_dataset_overview(state))
        story.extend(build_data_quality(state))
        story.extend(build_kpi_analysis(state))

        # Charts
        charts = state.get("visualization", {}).get("generated_files", [])
        if charts:
            from .pdf_styles import get_styles
            from reportlab.platypus import Paragraph, PageBreak

            styles = get_styles()
            story.append(Paragraph("Visualizations", styles["SectionTitle"]))
            story.extend(build_charts_section(charts))
            story.append(PageBreak())

        story.extend(build_insights_and_risks(state))
        story.extend(build_validation_summary(state))
        story.extend(build_appendix(state))

        # Build PDF
        doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)

        logger.info(f"ReportLab PDF successfully exported to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to generate ReportLab PDF: {e}")
        return ""
