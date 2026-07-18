# Tests

This folder contains the pytest suite for FinSight AI.

## Philosophy
- **Unit Tests**: Test logic isolated from the LLM.
- **Integration Tests**: Test the FastAPI endpoints using `TestClient`.

## Execution
```bash
python -m pytest backend/tests/ -v
```
