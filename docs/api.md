# API Documentation

The FinSight AI backend is built on FastAPI, providing a fully asynchronous and documented REST API. 

## Base URL
`/api/v1`

---

## 1. Upload Dataset
**`POST /upload`**
Uploads a CSV dataset, profiles its schema in the background, and prepares it for analysis.

**Request:**
- `multipart/form-data`
- Key: `file`, Value: `<CSV File>`

**Response (200 OK):**
```json
{
  "dataset_name": "sales_data.csv",
  "rows": 1500,
  "columns": 12,
  "file_size_bytes": 102400,
  "message": "File uploaded successfully"
}
```

---

## 2. Analyze Dataset
**`POST /analyze`**
Triggers the LangGraph workflow in a background thread. Returns a tracking ID immediately.

**Request:**
```json
{
  "filename": "sales_data.csv"
}
```

**Response (200 OK):**
```json
{
  "workflow_id": "24220d0d-6609-4c17-a20e-0106b065caab",
  "session_id": "7942d885-3d5f-4a18-a2db-fc081918c7a1",
  "status": "PENDING",
  "estimated_runtime": 45.0
}
```

---

## 3. Workflow Status
**`GET /workflow/{workflow_id}`**
Poll this endpoint to monitor the progression of the multi-agent graph.

**Response (200 OK):**
```json
{
  "workflow_id": "24220d0d-6609-4c17-a20e-0106b065caab",
  "status": "RUNNING",
  "current_agent": "Analytics Agent",
  "completed_agents": ["Auditor Agent", "Planner Agent"],
  "remaining_agents": ["Insight Agent", "Validation Agent", "Visualization Agent", "Report Agent"],
  "runtime": 12.5,
  "progress_percentage": 42.8
}
```

---

## 4. Artifact Retrieval
All generated outputs can be downloaded directly once the workflow status is `DONE`.

- **`GET /download/pdf/{workflow_id}`**: Returns `executive_report.pdf`
- **`GET /download/markdown/{workflow_id}`**: Returns `executive_report.md`
- **`GET /download/analytics/{workflow_id}`**: Returns JSON of deterministic mathematical outputs
- **`GET /download/all/{workflow_id}`**: Dynamically packages the entire `exports/workflows/{id}/` folder into a ZIP and returns it.

---

## Swagger UI
For interactive documentation, parameter schemas, and `Try It Out` capabilities, visit `http://127.0.0.1:8000/docs` while the server is running.
