"""
LangGraph Execution Runtime Policies.
Defines execution configurations and retry logic.
"""
import time
from typing import Callable, Any
from backend.utils.logger import logger

def with_retries(max_retries: int = 3, base_delay: float = 2.0) -> Callable:
    """Decorator for exponential backoff retries on LLM nodes."""
    def decorator(func: Callable) -> Callable:
        def wrapper(state: dict) -> Any:
            attempt = 0
            while attempt < max_retries:
                try:
                    return func(state)
                except Exception as e:
                    attempt += 1
                    if attempt == max_retries:
                        logger.error(f"Node {func.__name__} failed permanently after {max_retries} attempts.")
                        raise e
                    
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Node {func.__name__} failed (attempt {attempt}). Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator
