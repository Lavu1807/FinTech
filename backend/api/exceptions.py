from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.utils.logger import logger

class FinSightError(Exception):
    """Base exception for all custom FinSight AI errors."""
    pass

class DatasetValidationError(FinSightError):
    """Raised when the uploaded dataset is invalid."""
    pass

class LLMProviderError(FinSightError):
    """Raised when the LLM provider fails."""
    pass

class AgentExecutionError(FinSightError):
    """Raised when a specific LangGraph agent fails."""
    pass

def setup_exception_handlers(app: FastAPI):
    """
    Registers global exception handlers for consistent JSON error responses.
    """
    
    @app.exception_handler(FinSightError)
    async def finsight_error_handler(request: Request, exc: FinSightError):
        logger.error(f"FinSight Error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": exc.__class__.__name__, "message": str(exc)},
        )
        
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "ValidationError", "message": "Invalid request payload", "details": exc.errors()},
        )
        
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unexpected Error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "InternalServerError", "message": "An unexpected error occurred."},
        )
