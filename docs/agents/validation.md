# Validation Agent

The Validation Agent is a critical safety mechanism in FinSight AI. It acts as an autonomous auditor to ensure that the LLM (Insight Agent) did not hallucinate data in its narrative.

## Responsibilities
- **Fact-Checking**: Cross-references every numerical claim in `state["ai_insights"]` against the raw arrays in `state["business_analytics"]`.
- **Logic Verification**: Ensures that if the Insight Agent claims "revenue went up," the actual deterministic trend in the analytics is positive.

## Internal Modules
- `numerical_validator.py`: Regex-based extraction of numbers from text, verified against JSON arrays.
- `trend_validator.py`: Directional logic checker.

## I/O Contract
**Reads from State:**
- `state["ai_insights"]`
- `state["business_analytics"]`

**Writes to State:**
- `state["validation"]` (Contains a boolean `is_valid` and a list of `hallucinations` if any are found).

## LangGraph Routing
This agent has a conditional edge. If `state["validation"]["is_valid"]` is False, the LangGraph orchestrator routes the execution *back* to the Insight Agent with the hallucination report, forcing it to regenerate its summary.
