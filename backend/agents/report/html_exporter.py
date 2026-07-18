"""
Converts Markdown to Responsive HTML with corporate styling and Base64 embedded charts.
"""

import os
import base64
import markdown2
from jinja2 import Environment, FileSystemLoader
from backend.state.state import FinSightState


def _embed_base64_charts(md_text: str, state: FinSightState) -> str:
    """Finds chart references and embeds them as base64 images in HTML."""
    charts = state.get("visualization", {}).get("charts", [])
    if not charts:
        return md_text

    for chart in charts:
        path = chart.get("file_path")
        if path and os.path.exists(path):
            with open(path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode("utf-8")

            img_tag = f'<img src="data:image/png;base64,{b64_string}" class="chart-embed" alt="{chart.get("chart_title", "")}"/>'
            # We can append this to the markdown text under the respective chart title
            title = chart.get("chart_title", "")
            if title:
                md_text = md_text.replace(f"### {title}", f"### {title}\n\n{img_tag}\n")
    return md_text


def generate_html(md_text: str, state: FinSightState) -> str:
    # 1. Embed charts as Base64
    md_text_with_charts = _embed_base64_charts(md_text, state)

    # 2. Convert markdown to HTML
    body_html = markdown2.markdown(
        md_text_with_charts, extras=["tables", "fenced-code-blocks"]
    )

    # 3. Setup Jinja2
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))

    # 4. Load CSS and HTML template
    with open(os.path.join(template_dir, "report.css"), "r") as f:
        css = f.read()

    template = env.get_template("report.html")

    # 5. Render final HTML
    html = template.render(css=css, content=body_html)

    return html
