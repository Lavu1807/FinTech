from typing import Dict

from backend.state.state import FinSightState
from backend.utils.logger import logger

from .dashboard_assets import (
    get_css_styles,
    render_badge, 
    render_progress_bar, 
    render_kpi_cards, 
    render_charts, 
    render_narratives, 
    render_timeline,
    render_downloads
)
from .dashboard_templates import get_html_template

def generate_dashboard(state: FinSightState, downloads: Dict[str, str] = None) -> str:
    """Orchestrates the generation of the HTML dashboard from the FinSightState."""
    
    # 1. Extract Data
    dataset_name = state.get("dataset_info", {}).get("filename", "Dataset")
    business_domain = state.get("dataset_info", {}).get("business_domain", "Unknown Domain")
    quality_score = state.get("quality_metrics", {}).get("scores", {}).get("overall_quality_score", 0)
    
    workflow_tracking = state.get("workflow_tracking", {})
    planner_confidence = workflow_tracking.get("planner_confidence", 0.0) * 100
    
    business_analytics = state.get("business_analytics", {})
    kpis = business_analytics.get("calculated_kpis", {})
    
    visualization = state.get("visualization", {})
    charts_metadata = visualization.get("charts", [])
    chart_paths = [chart.get("file_path") for chart in charts_metadata if chart.get("file_path")]
    
    ai_insights = state.get("ai_insights", {})
    exec_summary = ai_insights.get("executive_summary", "")
    findings = ai_insights.get("key_findings", [])
    recommendations = ai_insights.get("recommendations", [])
    
    if isinstance(exec_summary, dict):
        exec_summary = exec_summary.get("executive_summary", "")
        if not findings:
            findings = exec_summary.get("key_findings", [])
        if not recommendations:
            recommendations = exec_summary.get("recommendations", [])
            
    validation = state.get("validation", {})
    hallucination_score = validation.get("hallucination_score", 0.0) * 100
    is_valid = validation.get("is_valid", True)
    
    agent_logs = state.get("agent_logs", [])
    
    # 2. Build Sidebar Content
    sidebar_html = f'''
    <div style="margin-bottom: 1rem;">
        <span class="text-secondary" style="font-size: 0.8rem;">Business Domain</span>
        <div style="font-weight: 500;">{business_domain}</div>
    </div>
    
    <div style="margin-bottom: 1rem;">
        <span class="text-secondary" style="font-size: 0.8rem;">Data Quality Score</span>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-weight: 500;">{quality_score}%</span>
            {render_badge("High" if quality_score > 80 else "Low", "success" if quality_score > 80 else "danger")}
        </div>
        {render_progress_bar(quality_score)}
    </div>
    
    <div style="margin-bottom: 1rem;">
        <span class="text-secondary" style="font-size: 0.8rem;">Planner Confidence</span>
        <div style="font-weight: 500;">{planner_confidence:.1f}%</div>
        {render_progress_bar(planner_confidence)}
    </div>
    
    <div style="margin-bottom: 1rem;">
        <span class="text-secondary" style="font-size: 0.8rem;">Validation Status</span>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-weight: 500;">Score: {hallucination_score}%</span>
            {render_badge("Valid" if is_valid else "Flagged", "success" if is_valid else "danger")}
        </div>
    </div>
    '''
    
    # 3. Build Main Content Sections
    downloads_content = render_downloads(downloads or {})
    kpi_content = render_kpi_cards(kpis)
    charts_content = render_charts(chart_paths)
    
    narrative_content = ""
    if exec_summary:
        narrative_content += f'<div class="glass-card" style="margin-bottom: 2rem;"><h3 style="margin-bottom: 1rem;">Executive Summary</h3><p class="text-secondary">{exec_summary}</p></div>'
        
    narrative_content += render_narratives("Key Findings", "🔍", findings)
    narrative_content += render_narratives("Recommendations", "💡", recommendations)
    
    timeline_content = render_timeline(agent_logs)
    
    # 4. Assemble HTML
    css = get_css_styles()
    html = get_html_template(
        css=css,
        sidebar_content=sidebar_html,
        downloads_content=downloads_content,
        kpi_content=kpi_content,
        charts_content=charts_content,
        narrative_content=narrative_content,
        timeline_content=timeline_content,
        dataset_name=dataset_name
    )
    
    return html

def export_html_dashboard(state: FinSightState, downloads: Dict[str, str] = None, workflow_id: str = None) -> str:
    """Generates the HTML dashboard and saves it to the exports directory."""
    try:
        html = generate_dashboard(state, downloads)
        
        if not workflow_id:
            workflow_id = state.get("execution_metadata", {}).get("workflow_id", "unknown")
            
        from backend.services.artifact_manager import ArtifactManager
        artifact_mgr = ArtifactManager(workflow_id)
        
        file_path = artifact_mgr.save_text("dashboard", "Dashboard.html", html)
            
        logger.info(f"HTML Dashboard successfully exported to {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Failed to generate HTML Dashboard: {e}")
        return ""
