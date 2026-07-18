# FinSight API Reference

The FinSight API is structured around RESTful endpoints available under the `/api/v1` prefix.

## 1. System Health
- `GET /api/v1/health`: Comprehensive system health, checking LLM availability and write permissions.
- `GET /api/v1/health/live`: Liveness probe for load balancers.
- `GET /api/v1/health/ready`: Readiness probe verifying system dependencies.

## 2. Workflow Orchestration
- `POST /api/v1/workflow/upload`: Upload a CSV dataset.
- `POST /api/v1/workflow/analyze`: Trigger the LangGraph background execution.
- `GET /api/v1/workflow/status/{workflow_id}`: Poll for the workflow progress.

## 3. Observability Dashboard
- `GET /api/v1/dashboard`: Full dashboard payload.
- `GET /api/v1/dashboard/summary`: High-level metrics.
- `GET /api/v1/dashboard/timeline`: Chronological execution events.
- `GET /api/v1/dashboard/metrics`: Cost and performance analysis.

## 4. Artifact Downloads
- `GET /api/v1/downloads/report/pdf`: Download the PDF report.
- `GET /api/v1/downloads/report/markdown`: Download the Markdown report.
- `GET /api/v1/downloads/archive`: Download a ZIP archive containing all reports, charts, and metrics.
