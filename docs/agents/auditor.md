# Auditor Agent

The Auditor Agent is the first node in the FinSight AI LangGraph workflow. It acts as the data quality gateway, ensuring that the raw dataset is safe, clean, and structurally sound before any business logic or LLM processing occurs.

## Responsibilities
- **Schema Profiling**: Determines column data types, missing values, and unique counts.
- **PII Detection**: Scans string columns for Personally Identifiable Information (Emails, SSNs, Credit Cards) using Regex and heuristics.
- **Data Quality Scoring**: Calculates a deterministic percentage score of the dataset's health.

## Internal Modules
- `profiler.py`: Pandas engine for statistical extraction.
- `quality.py`: Evaluator for completeness and consistency.

## I/O Contract
**Reads from State:**
- `state["dataset_info"]["raw_dataframe"]`

**Writes to State:**
- `state["dataset_profile"]` (JSON schema map)
- `state["quality_metrics"]`
- `state["dataset_risks"]` (List of strings, e.g., "High missing value ratio in 'Age'")

## Time Complexity
- Profiling operations scale at `O(N * C)` where N is rows and C is columns.
- Vectorized Pandas methods are utilized to ensure < 1s latency on 100k rows.

## Failure Handling
If the data quality score falls below 40%, or if critical PII is detected, the Auditor Agent flags the dataset as invalid and triggers an early exit from the LangGraph workflow.
