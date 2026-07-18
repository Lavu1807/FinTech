# Report Agent

The Report Agent is the final node in the FinSight AI pipeline. It acts as the compiler, aggregating all state variables into cohesive final artifacts.

## Responsibilities
- Compiles the narratives from the Insight Agent, the paths from the Visualization Agent, and the telemetry from the Execution Metadata.
- Renders a master Markdown document.
- Converts the Markdown into a styled PDF.

## I/O Contract
**Reads from State:**
- `state["ai_insights"]`
- `state["visualization"]`
- `state["execution_metadata"]`

**Writes to State:**
- `state["reports"]` (Contains paths to the final PDF and MD files).

## Output Mechanism
Uses a Jinja2 templating system to inject JSON state variables into a predefined Markdown scaffold. It then uses `pdfkit` (wrapper for `wkhtmltopdf`) to generate the final PDF report.
