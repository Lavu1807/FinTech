from reportlab.platypus import Paragraph, Spacer, Table, PageBreak
from reportlab.lib.units import inch
from typing import Dict, Any

from .pdf_styles import get_styles, get_table_style, get_kpi_grid_style

def _dict_to_list(d: dict, depth=0) -> str:
    """Flattens a dictionary to a string for simple display."""
    items = []
    for k, v in d.items():
        if isinstance(v, dict):
            items.append(f"{'  '*depth}• {k}:")
            items.append(_dict_to_list(v, depth+1))
        else:
            if isinstance(v, float):
                v = f"{v:.2f}"
            items.append(f"{'  '*depth}• {k}: {v}")
    return "\n".join(items)

def build_cover_page(dataset_name: str, workflow_id: str, generation_date: str) -> list:
    styles = get_styles()
    story = [
        Spacer(1, 2*inch),
        Paragraph("FinSight AI", styles['CoverTitle']),
        Paragraph("Enterprise Business Intelligence Report", styles['CoverSubtitle']),
        Spacer(1, 1*inch),
        Paragraph("Prepared For", styles['SubsectionTitle']),
        Paragraph("ABC Corporation", styles['BodyTextCustom']),
        Spacer(1, 0.5*inch),
        Paragraph("Generated", styles['SubsectionTitle']),
        Paragraph(generation_date, styles['BodyTextCustom']),
        Spacer(1, 0.5*inch),
        Paragraph("Workflow ID", styles['SubsectionTitle']),
        Paragraph(workflow_id, styles['BodyTextCustom']),
        PageBreak()
    ]
    return story

def build_executive_summary(state: Dict[str, Any]) -> list:
    styles = get_styles()
    dataset_info = state.get("dataset_info", {})
    quality_score = state.get("quality_metrics", {}).get("scores", {}).get("overall_quality_score", 0)
    validation = state.get("validation", {})
    confidence = state.get("workflow_tracking", {}).get("planner_confidence", 0) * 100
    
    grade = "A" if quality_score > 90 else "B" if quality_score > 80 else "C" if quality_score > 70 else "D"
    status = "PASSED" if validation.get("is_valid", True) else "FLAGGED"
    
    story = [
        Paragraph("Executive Summary", styles['SectionTitle']),
        Spacer(1, 0.2*inch)
    ]
    
    data = [
        ["Dataset", dataset_info.get("filename", "N/A")],
        ["Business Domain", dataset_info.get("business_domain", "Unknown")],
        ["Quality Grade", grade],
        ["Planner Confidence", f"{confidence:.1f}%"],
        ["Overall Validation", status]
    ]
    
    t = Table(data, colWidths=[2.5*inch, 4*inch])
    t.setStyle(get_table_style())
    
    story.append(t)
    story.append(Spacer(1, 0.5*inch))
    
    exec_summary = state.get("ai_insights", {}).get("executive_summary", "")
    if isinstance(exec_summary, dict):
        exec_summary = exec_summary.get("executive_summary", "")
        
    if exec_summary:
        story.append(Paragraph(str(exec_summary).replace("\n", "<br/>"), styles['BodyTextCustom']))
        
    story.append(PageBreak())
    return story

def build_dataset_overview(state: Dict[str, Any]) -> list:
    styles = get_styles()
    profile = state.get("dataset_profile", {})
    
    story = [Paragraph("Dataset Overview", styles['SectionTitle'])]
    
    if not profile:
        story.append(Paragraph("Dataset profile not available.", styles['BodyTextCustom']))
        story.append(PageBreak())
        return story
        
    data = [["Metric", "Value"]]
    data.append(["Rows", str(profile.get("num_rows", 0))])
    data.append(["Columns", str(profile.get("num_cols", 0))])
    data.append(["Missing Values", str(profile.get("missing_cells", 0))])
    data.append(["Duplicate Rows", str(profile.get("duplicate_rows", 0))])
    data.append(["Numeric Columns", str(len(profile.get("numeric_columns", [])))])
    data.append(["Categorical Columns", str(len(profile.get("categorical_columns", [])))])
    
    t = Table(data, colWidths=[3*inch, 3*inch])
    t.setStyle(get_table_style())
    story.append(t)
    story.append(PageBreak())
    return story

def build_data_quality(state: Dict[str, Any]) -> list:
    styles = get_styles()
    scores = state.get("quality_metrics", {}).get("scores", {})
    
    story = [Paragraph("Data Quality Assessment", styles['SectionTitle'])]
    
    if not scores:
        story.append(Paragraph("Quality assessment not available.", styles['BodyTextCustom']))
        story.append(PageBreak())
        return story
        
    data = [["Metric", "Score"]]
    for k, v in scores.items():
        data.append([k.replace('_', ' ').title(), f"{v:.1f}%" if isinstance(v, (int, float)) else str(v)])
        
    t = Table(data, colWidths=[3*inch, 3*inch])
    t.setStyle(get_table_style())
    story.append(t)
    story.append(PageBreak())
    return story

def build_kpi_analysis(state: Dict[str, Any]) -> list:
    styles = get_styles()
    kpis = state.get("business_analytics", {}).get("calculated_kpis", {})
    
    story = [Paragraph("KPI Analysis", styles['SectionTitle'])]
    
    if not kpis:
        story.append(Paragraph("No KPIs available.", styles['BodyTextCustom']))
        story.append(PageBreak())
        return story
        
    for k, v in kpis.items():
        title = k.replace('_', ' ').title()
        val = list(v.values())[0] if isinstance(v, dict) and v else v
        
        if isinstance(val, float):
            val = f"{val:.2f}"
            
        data = [[title], [str(val)]]
        t = Table(data, colWidths=[6*inch])
        t.setStyle(get_kpi_grid_style())
        story.append(t)
        story.append(Spacer(1, 0.25*inch))
        
    story.append(PageBreak())
    return story

def build_insights_and_risks(state: Dict[str, Any]) -> list:
    styles = get_styles()
    story = []
    
    ai_insights = state.get("ai_insights", {})
    exec_summary = ai_insights.get("executive_summary", {})
    
    findings = ai_insights.get("key_findings", [])
    recommendations = ai_insights.get("recommendations", [])
    
    if isinstance(exec_summary, dict):
        if not findings:
            findings = exec_summary.get("key_findings", [])
        if not recommendations:
            recommendations = exec_summary.get("recommendations", [])
            
    # Insights
    story.append(Paragraph("Business Insights", styles['SectionTitle']))
    if findings:
        for f in findings:
            if isinstance(f, dict):
                f = str(f)
            story.append(Paragraph(f, styles['BulletCustom']))
    else:
        story.append(Paragraph("No insights generated.", styles['BodyTextCustom']))
    story.append(Spacer(1, 0.5*inch))
    
    # Risks
    story.append(Paragraph("Business Risks", styles['SectionTitle']))
    risks = state.get("dataset_risks", [])
    if risks:
        for r in risks:
            if isinstance(r, dict):
                r = r.get("description", str(r))
            story.append(Paragraph(str(r), styles['BulletCustom']))
    else:
        story.append(Paragraph("No risks detected.", styles['BodyTextCustom']))
    story.append(Spacer(1, 0.5*inch))
    
    # Recommendations
    story.append(Paragraph("Recommendations", styles['SectionTitle']))
    if recommendations:
        for r in recommendations:
            if isinstance(r, dict):
                r = str(r)
            story.append(Paragraph(r, styles['BulletCustom']))
    else:
        story.append(Paragraph("No recommendations provided.", styles['BodyTextCustom']))
        
    story.append(PageBreak())
    return story

def build_validation_summary(state: Dict[str, Any]) -> list:
    styles = get_styles()
    validation = state.get("validation", {})
    
    story = [Paragraph("Validation Summary", styles['SectionTitle'])]
    
    if not validation:
        story.append(Paragraph("No validation data available.", styles['BodyTextCustom']))
        story.append(PageBreak())
        return story
        
    data = [["Metric", "Value"]]
    data.append(["Overall Status", "PASSED" if validation.get("is_valid") else "FLAGGED"])
    data.append(["Hallucination Score", f"{validation.get('hallucination_score', 0)*100:.1f}%"])
    
    t = Table(data, colWidths=[3*inch, 3*inch])
    t.setStyle(get_table_style())
    story.append(t)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Validation Logs:", styles['SubsectionTitle']))
    for log in validation.get("validation_logs", []):
        story.append(Paragraph(str(log), styles['BulletCustom']))
        
    story.append(PageBreak())
    return story

def build_appendix(state: Dict[str, Any]) -> list:
    styles = get_styles()
    meta = state.get("execution_metadata", {})
    
    story = [Paragraph("Appendix & Workflow Detail", styles['SectionTitle'])]
    
    data = [["Metric", "Value"]]
    data.append(["Workflow ID", meta.get("workflow_id", "N/A")])
    data.append(["Execution Time", f"{meta.get('total_execution_time', 0):.2f} seconds"])
    data.append(["LLM Calls", str(meta.get("total_llm_calls", 0))])
    data.append(["Total Tokens", str(meta.get("total_tokens", 0))])
    data.append(["Prompt Version", meta.get("prompt_version", "N/A")])
    
    t = Table(data, colWidths=[3*inch, 3*inch])
    t.setStyle(get_table_style())
    story.append(t)
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Agent Execution Logs", styles['SubsectionTitle']))
    
    for agent in state.get("agent_logs", []):
        name = agent.get('agent_name', 'Unknown')
        status = agent.get('status', 'N/A')
        time = agent.get('timestamp', '')
        if isinstance(time, str):
            time_str = time
        else:
            try:
                time_str = time.strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_str = str(time)
        story.append(Paragraph(f"<b>{name}</b> [{status}] - {time_str}", styles['BodyTextCustom']))
        
    return story
