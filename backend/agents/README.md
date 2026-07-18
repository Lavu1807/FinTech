# Agents

This directory contains the core intelligence nodes for the FinSight AI LangGraph workflow.

## The Nodes
Each folder represents an independent execution step in the graph:
- **Auditor**: Data profiling.
- **Planner**: Strategic execution generation.
- **Analytics**: Pandas mathematical sandbox (No LLM).
- **Insight**: LLM narrative generation.
- **Validation**: Hallucination detection.
- **Visualization**: Matplotlib chart generation (No LLM).
- **Report**: Artifact compilation (No LLM).

Agents do not communicate directly. They read from and write to the shared `FinSightState`.
