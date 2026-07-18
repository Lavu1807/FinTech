# Planner Agent

The Planner Agent acts as the strategic brain of the workflow. Instead of generating insights immediately, it reviews the Auditor's profile and formulates a deterministic execution plan.

## Responsibilities
- Decides which business analytics modules are necessary (e.g., Time Series vs. Cohort Analysis) based on the available columns.
- Specifies exact aggregation dimensions and metrics for the Analytics Agent to compute.

## I/O Contract
**Reads from State:**
- `state["dataset_profile"]`
- `state["dataset_info"]["business_domain"]`

**Writes to State:**
- `state["workflow_tracking"]["analysis_plan"]`
- `state["workflow_tracking"]["required_agents"]`

## LLM Strategy
This node utilizes the `mistral-large-latest` model via the `LLMGateway` utilizing `Instructor` to ensure the LLM strictly adheres to the `AnalysisPlan` Pydantic model. 

## Failure Handling
If the LLM fails to return a valid JSON plan, the request is retried up to 3 times. If it continually fails, a fallback deterministic heuristic plan is generated based on standard grouping methodologies.
