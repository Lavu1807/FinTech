# Architectural Guidelines: FinSight AI

- **Backend First:** FinSight is a backend-first, API-first enterprise AI platform.
- **NO FRONTEND:** Do not create UI code (React, Vue, Streamlit, HTML dashboards). Users interact strictly via FastAPI endpoints, JSON, and generated file exports.
- **Production Engineering:** Prefer FastAPI, Pydantic, Typed models, Strategy/Factory Patterns, Dependency Injection, SOLID Principles, comprehensive logging, and graceful error handling.
- **Maintain Current Architecture:** Do not modify existing agent responsibilities, LangGraph logic, prompt templates, or deterministic analytics unless explicitly asked. Focus on robustness, observability, and explainability.
