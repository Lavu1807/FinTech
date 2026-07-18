"""
FastAPI Dependencies for dependency injection.
"""
from typing import Generator
from backend.database.session import SessionLocal

def get_db() -> Generator:
    """
    Dependency to provide a database session to FastAPI route handlers.
    Ensures that the session is closed after the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
