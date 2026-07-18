from typing import Dict, Any


def generate_trace_html(
    agent_trace: Dict[str, Any], workflow_timeline: Dict[str, Any], dataset_name: str
) -> str:
    """
    Generates a standalone Trace.html page for the Workflow Trace.
    Provides a visual UI for the execution timeline, critical path, and agent metrics.
    """

    # 1. CSS Styles
    css = """
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
        --border-color: rgba(255, 255, 255, 0.1);
        --glass-border: 1px solid rgba(255, 255, 255, 0.05);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
    body { background-color: var(--bg-main); color: var(--text-primary); line-height: 1.6; padding: 2rem; }
    .header { margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: var(--glass-border); padding-bottom: 1rem; }
    .header h1 { font-size: 1.8rem; background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    .glass-card { background: var(--bg-card); backdrop-filter: blur(12px); border: var(--glass-border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }
    h3 { font-size: 1.2rem; margin-bottom: 1rem; color: var(--accent-blue); }
    
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
    .metric-box { padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px; border-left: 3px solid var(--accent-purple); }
    .metric-label { font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; }
    .metric-val { font-size: 1.4rem; font-weight: 600; margin-top: 0.3rem; }
    
    /* Timeline Node Styles */
    .timeline { position: relative; padding-left: 2rem; margin-top: 1rem; }
    .timeline::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 2px; background: var(--border-color); }
    .node { position: relative; margin-bottom: 1.5rem; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px; }
    .node::before { content: ''; position: absolute; left: -2.4rem; top: 1.2rem; width: 12px; height: 12px; border-radius: 50%; background: var(--accent-blue); border: 2px solid var(--bg-main); }
    .node-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
    .node-title { font-weight: 600; font-size: 1.1rem; }
    .node-status { font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 4px; background: rgba(16,185,129,0.2); color: var(--accent-green); }
    .node-status.FAILED { background: rgba(239,68,68,0.2); color: var(--accent-red); }
    .node-stats { display: flex; gap: 1rem; font-size: 0.85rem; color: var(--text-secondary); }
    .node-warnings { margin-top: 0.5rem; font-size: 0.85rem; color: var(--accent-red); background: rgba(239,68,68,0.1); padding: 0.5rem; border-radius: 4px; border-left: 2px solid var(--accent-red); }
    
    .nav-btn { background: rgba(59,130,246,0.1); color: var(--accent-blue); padding: 0.5rem 1rem; text-decoration: none; border-radius: 6px; font-weight: 500; transition: 0.2s; }
    .nav-btn:hover { background: rgba(59,130,246,0.2); }
    """

    # 2. Extract Data
    summary = workflow_timeline.get("execution_summary", {})
    timeline = workflow_timeline.get("timeline", [])
    critical_path = workflow_timeline.get("critical_path", [])

    # 3. Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinSight AI - Workflow Trace</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>{css}</style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Workflow Trace</h1>
            <p class="text-secondary">Deterministic Agent Execution Log for <strong>{dataset_name}</strong></p>
        </div>
        <a href="Dashboard.html" class="nav-btn">← Back to Dashboard</a>
    </div>
    
    <div class="glass-card">
        <h3>Execution Metrics</h3>
        <div class="grid-3">
            <div class="metric-box">
                <div class="metric-label">Total Execution Time</div>
                <div class="metric-val">{summary.get("total_execution_time", 0):.2f}s</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Total LLM Calls</div>
                <div class="metric-val">{summary.get("total_llm_calls", 0)}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Token Usage</div>
                <div class="metric-val">{summary.get("total_tokens", 0):,}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Estimated Cost</div>
                <div class="metric-val">${summary.get("total_estimated_cost", 0.0):.4f}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Slowest Agent</div>
                <div class="metric-val">{summary.get("slowest_agent", "N/A")}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Fastest Agent</div>
                <div class="metric-val">{summary.get("fastest_agent", "N/A")}</div>
            </div>
        </div>
    </div>
    
    <div class="glass-card">
        <h3>Critical Path</h3>
        <div style="font-family: monospace; background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 6px; color: var(--accent-green);">
            {' → '.join(critical_path)}
        </div>
    </div>

    <div class="glass-card">
        <h3>Agent Execution Timeline</h3>
        <div class="timeline">
    """

    for node in timeline:
        status_class = "FAILED" if node.get("status") == "FAILED" else "SUCCESS"
        warnings_html = ""
        if node.get("warnings"):
            warn_list = "<br/>".join(node["warnings"])
            warnings_html = f"<div class='node-warnings'>⚠️ {warn_list}</div>"

        html += f"""
            <div class="node">
                <div class="node-header">
                    <span class="node-title">{node.get("agent", "Unknown")}</span>
                    <span class="node-status {status_class}">{node.get("status", "COMPLETED")}</span>
                </div>
                <div class="node-stats">
                    <span>⏱️ {node.get("duration", 0):.2f}s</span>
                    <span>🧠 Provider: {node.get("provider", "N/A")}</span>
                    <span>📞 {node.get("llm_calls", 0)} Calls</span>
                    <span>🪙 {node.get("token_usage", 0):,} Tokens</span>
                    <span>💰 ${node.get("estimated_cost", 0.0):.4f}</span>
                </div>
                {warnings_html}
            </div>
        """

    html += """
        </div>
    </div>
</body>
</html>
    """
    return html
