"""
Pydantic schemas for the Report Generator Agent.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class ReportOutput(BaseModel):
    executive_summary: str
    markdown_report_path: str
    pdf_report_path: Optional[str] = None
    html_report_path: str
    dashboard_html_path: Optional[str] = None
    report_manifest: Dict[str, Any]
