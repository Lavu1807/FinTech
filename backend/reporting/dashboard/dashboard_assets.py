import base64
from pathlib import Path
from typing import Dict, Any, List

def render_badge(text: str, level: str = "info") -> str:
    """Renders a status badge."""
    valid_levels = {"success", "warning", "danger", "info"}
    level = level if level in valid_levels else "info"
    return f'<span class="badge badge-{level}">{text}</span>'

def render_progress_bar(percentage: float) -> str:
    """Renders a gradient progress bar."""
    pct = max(0, min(100, percentage))
    return f'''
    <div class="progress-container">
        <div class="progress-bar" style="width: {pct}%;"></div>
    </div>
    '''

def render_kpi_cards(kpis: Dict[str, Any]) -> str:
    """Renders KPI metrics into grid cards."""
    if not kpis:
        return "<p class='text-secondary'>No KPI metrics available.</p>"
        
    html = '<div class="kpi-grid">'
    for label, value in kpis.items():
        if isinstance(value, dict):
            continue
            
        display_val = value
            
        # Format numbers if possible
        try:
            if isinstance(display_val, (int, float)):
                if abs(display_val) > 1000000:
                    display_val = f"{display_val/1000000:.2f}M"
                elif abs(display_val) > 1000:
                    display_val = f"{display_val/1000:.1f}K"
                elif isinstance(display_val, float):
                    display_val = f"{display_val:.2f}"
        except:
            pass
            
        html += f'''
        <div class="glass-card">
            <div class="kpi-label">{str(label).replace('_', ' ')}</div>
            <div class="kpi-value">{display_val}</div>
        </div>
        '''
    html += '</div>'
    return html

def render_charts(chart_paths: List[str]) -> str:
    """Reads PNG files and embeds them as Base64 strings in the HTML."""
    if not chart_paths:
        return "<p class='text-secondary'>No visual charts generated.</p>"
        
    html = '<div class="chart-grid">'
    for path_str in chart_paths:
        p = Path(path_str)
        if p.exists() and p.suffix.lower() == '.png':
            try:
                with open(p, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                img_src = f"data:image/png;base64,{b64}"
                title = p.stem.replace('_', ' ').title()
                
                html += f'''
                <div class="glass-card chart-container">
                    <h4 style="color: #333; margin-bottom: 1rem; border-bottom: 1px solid #eee; padding-bottom: 0.5rem;">{title}</h4>
                    <img class="chart-img" src="{img_src}" alt="{title}" />
                </div>
                '''
            except Exception as e:
                html += f"<p>Error loading chart {p.name}: {e}</p>"
    html += '</div>'
    return html

def render_narratives(title: str, icon: str, items: List[str]) -> str:
    """Renders narrative arrays into styled list cards."""
    if not items:
        return ""
        
    if isinstance(items, str):
        items = [items]
        
    html = f'<h3 class="section-title">{title}</h3><div class="narrative-grid">'
    for item in items:
        html += f'''
        <div class="narrative-item">
            <div class="narrative-icon">{icon}</div>
            <div class="narrative-content">
                <p>{item}</p>
            </div>
        </div>
        '''
    html += '</div>'
    return html

def render_timeline(agent_logs: List[Dict[str, Any]]) -> str:
    """Renders the execution timeline of agents."""
    if not agent_logs:
        return "<p class='text-secondary'>No execution logs available.</p>"
        
    html = '<div class="timeline">'
    for log in agent_logs:
        name = log.get('agent_name', 'Unknown Agent')
        status = log.get('status', 'COMPLETED')
        msg = log.get('message', '')
        calls = log.get('llm_calls', 0)
        provider = log.get('provider_used', 'N/A')
        
        badge = render_badge(status, "success" if status == "COMPLETED" else "danger")
        
        html += f'''
        <div class="timeline-item">
            <div class="timeline-title">
                <span>{name}</span>
                {badge}
            </div>
            <div class="timeline-meta">
                {msg}<br/>
                Provider: {provider} | LLM Calls: {calls}
            </div>
        </div>
        '''
    html += '</div>'
    return html

def render_downloads(downloads: Dict[str, str]) -> str:
    """Renders download buttons/links for available artifacts."""
    if not downloads:
        return ""
        
    html = '<h3 class="section-title">Downloads</h3><div class="kpi-grid">'
    for label, path in downloads.items():
        if path:
            html += f'''
            <div class="glass-card" style="display: flex; align-items: center; justify-content: space-between;">
                <div class="kpi-label">{label}</div>
                <a href="{path}" target="_blank" style="color: var(--accent-blue); text-decoration: none; font-weight: 500; padding: 0.25rem 0.5rem; background: rgba(59,130,246,0.1); border-radius: 4px;">Download ⬇️</a>
            </div>
            '''
    html += '</div>'
    return html

def get_css_styles() -> str:
    """Returns modern, sleek CSS for the FinSight AI Dashboard."""
    return """
    :root {
        --bg-main: #0f172a;
        --bg-panel: #1e293b;
        --bg-card: rgba(30, 41, 59, 0.7);
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-yellow: #f59e0b;
        --border-color: rgba(255, 255, 255, 0.1);
        --glass-border: 1px solid rgba(255, 255, 255, 0.05);
        --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        --radius-lg: 16px;
        --radius-md: 12px;
        --radius-sm: 8px;
    }

    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    body {
        background-color: var(--bg-main);
        color: var(--text-primary);
        line-height: 1.6;
        overflow-x: hidden;
    }

    /* Layout */
    .dashboard-container {
        display: grid;
        grid-template-columns: 280px 1fr;
        min-height: 100vh;
    }

    .sidebar {
        background-color: var(--bg-panel);
        border-right: var(--glass-border);
        padding: 2rem;
        display: flex;
        flex-direction: column;
        gap: 2rem;
        position: sticky;
        top: 0;
        height: 100vh;
        overflow-y: auto;
    }

    .main-content {
        padding: 2rem 3rem;
        max-width: 1400px;
        margin: 0 auto;
        width: 100%;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: var(--glass-border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--glass-shadow);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45);
    }

    /* Typography */
    h1, h2, h3, h4 {
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }

    .section-title {
        margin: 2.5rem 0 1.5rem 0;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.75rem;
    }

    /* KPI Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: var(--accent-blue);
    }
    
    .kpi-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Charts */
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
        gap: 1.5rem;
    }
    
    .chart-container {
        width: 100%;
        border-radius: var(--radius-md);
        overflow: hidden;
        background: #fff; /* White bg for matplotlib charts */
        padding: 1rem;
    }
    
    .chart-img {
        width: 100%;
        height: auto;
        display: block;
    }

    /* Narrative Cards */
    .narrative-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .narrative-item {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: var(--radius-md);
        border-left: 4px solid var(--accent-purple);
    }
    
    .narrative-icon {
        font-size: 1.25rem;
        background: rgba(139, 92, 246, 0.2);
        padding: 0.5rem;
        border-radius: 50%;
        color: var(--accent-purple);
    }
    
    .narrative-content h4 {
        margin-bottom: 0.25rem;
        font-size: 1rem;
    }
    
    .narrative-content p {
        color: var(--text-secondary);
        font-size: 0.95rem;
    }

    /* Progress Bars & Badges */
    .progress-container {
        width: 100%;
        background-color: rgba(255,255,255,0.1);
        border-radius: 999px;
        height: 8px;
        margin-top: 0.5rem;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
        transition: width 1s ease-out;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-success { background: rgba(16, 185, 129, 0.2); color: var(--accent-green); }
    .badge-warning { background: rgba(245, 158, 11, 0.2); color: var(--accent-yellow); }
    .badge-danger { background: rgba(239, 68, 68, 0.2); color: var(--accent-red); }
    .badge-info { background: rgba(59, 130, 246, 0.2); color: var(--accent-blue); }

    /* Timeline */
    .timeline {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .timeline-item {
        position: relative;
        padding-left: 2rem;
        padding-bottom: 1rem;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 2px;
        background: var(--border-color);
    }
    
    .timeline-item::after {
        content: '';
        position: absolute;
        left: -4px;
        top: 0.25rem;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--accent-blue);
        border: 2px solid var(--bg-main);
    }
    
    .timeline-item:last-child::before {
        display: none;
    }
    
    .timeline-title {
        font-weight: 600;
        display: flex;
        justify-content: space-between;
    }
    
    .timeline-meta {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }

    /* Print Styles */
    @media print {
        body { background: white; color: black; }
        .dashboard-container { display: block; }
        .sidebar { display: none; }
        .main-content { padding: 0; max-width: 100%; }
        .glass-card { 
            background: white; 
            border: 1px solid #ddd; 
            box-shadow: none; 
            page-break-inside: avoid;
        }
        .gradient-text { background: none; -webkit-text-fill-color: black; color: black; }
        h1, h2, h3, h4 { color: black; }
        .text-secondary { color: #555; }
        .chart-container { background: white; border: 1px solid #eee; }
    }
    
    /* Responsive */
    @media (max-width: 1024px) {
        .dashboard-container { grid-template-columns: 1fr; }
        .sidebar { 
            position: relative; 
            height: auto; 
            border-right: none; 
            border-bottom: var(--glass-border); 
            padding: 1.5rem;
        }
        .main-content { padding: 1.5rem; }
        .chart-grid { grid-template-columns: 1fr; }
    }
    """
