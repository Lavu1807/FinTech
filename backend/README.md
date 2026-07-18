# Backend

This folder contains the core enterprise implementation of FinSight AI.

## Structure
- **`agents/`**: The LangGraph AI nodes.
- **`api/`**: The FastAPI server, routers, and Pydantic schemas.
- **`config/`**: Global settings and `.env` parsers.
- **`graph/`**: The state machine and orchestrator.
- **`services/`**: External gateway integrations (LLMs).
- **`utils/`**: Exporters and helper scripts.
- **`tests/`**: Pytest suite.

FinSight AI is designed as an API-first backend. Do not place frontend code here.
