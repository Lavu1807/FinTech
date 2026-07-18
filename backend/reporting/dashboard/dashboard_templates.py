def get_html_template(
    css: str,
    sidebar_content: str,
    downloads_content: str,
    kpi_content: str,
    charts_content: str,
    narrative_content: str,
    timeline_content: str,
    dataset_name: str
) -> str:
    """Returns the master HTML5 template for the dashboard."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinSight AI Dashboard - {dataset_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        {css}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div>
                <h1 class="gradient-text">FinSight AI</h1>
                <p class="text-secondary" style="font-size: 0.875rem;">Enterprise Analytics Copilot</p>
            </div>
            
            <div class="glass-card">
                <h3 style="font-size: 1rem; margin-bottom: 1rem;">Execution Summary</h3>
                {sidebar_content}
            </div>

            <div class="glass-card" style="margin-top: auto;">
                <h3 style="font-size: 1rem; margin-bottom: 1rem;">Workflow Timeline</h3>
                {timeline_content}
            </div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <header style="margin-bottom: 2rem;">
                <h2>Dataset: <span style="color: var(--accent-blue)">{dataset_name}</span></h2>
                <p class="text-secondary">Automated Business Intelligence Analysis</p>
            </header>

            <section>
                {downloads_content}
            </section>

            <section>
                {kpi_content}
            </section>

            <section>
                <h3 class="section-title">Visualizations</h3>
                {charts_content}
            </section>

            <section>
                {narrative_content}
            </section>
        </main>
    </div>
</body>
</html>
"""
