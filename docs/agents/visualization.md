# Visualization Agent

The Visualization Agent is a deterministically driven plotting engine. It converts the Pandas aggregations into publication-ready charts.

## Responsibilities
- Selects the most appropriate chart type (Bar, Line, Heatmap) based on the shape of the data.
- Renders SVGs and PNGs using Matplotlib and Seaborn.
- Saves the files to the `exports/workflows/{workflow_id}/charts/` directory.

## I/O Contract
**Reads from State:**
- `state["business_analytics"]`
- `state["dataset_profile"]`

**Writes to State:**
- `state["visualization"]` (A manifest of filepaths to the generated charts).

## Implementation Details
The LLM is completely excluded from this node. Plotting is handled by a factory pattern in `backend/agents/visualization/` that dynamically consumes the JSON output of the Analytics Agent.

## Failure Handling
Matplotlib exceptions are caught globally. If a chart fails to render due to invalid dimensionality, the agent gracefully skips that specific visualization and continues, logging a warning to the telemetry engine.
