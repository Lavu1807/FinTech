# FinSight AI Architecture

FinSight AI is a multi-agent financial intelligence copilot orchestrated using LangGraph and exposed via FastAPI.

## Core Agents
1. **Auditor Agent**: Analyzes data quality, column semantics, and detects PII.
2. **Planner Agent**: Generates an execution plan based on the data profile.
3. **Analytics Agent**: Computes deterministic statistics (trend, segment, correlation) using Pandas.
4. **Insight Agent**: Explains the deterministic analytics using LLMs.
5. **Validation Agent**: Evaluates the LLM insights against the deterministic facts for hallucinations.
6. **Visualization Agent**: Selects chart strategies and generates Matplotlib graphs.
7. **Report Agent**: Compiles findings into PDF and Markdown exports.

## Execution Flow
The execution flow strictly follows the order defined above. The shared state is managed by a strongly typed `FinSightState` dictionary containing metrics, profiling data, analytics results, and execution telemetry. No agent overwrites another agent's core data.
