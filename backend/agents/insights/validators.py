"""
Security Validators for Insight Agent.
Prevents leaking raw DataFrames or PII to the LLM context.
"""
import re
from backend.utils.logger import logger

def validate_context_safety(context_str: str) -> bool:
    """Returns True if safe, False if risky patterns are found."""
    # Check for DataFrame serialization patterns
    if "DataFrame" in context_str or "pandas.core.frame" in context_str:
        logger.error("InsightValidator: Raw Pandas object detected in context.")
        return False
        
    # Check for unredacted emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.search(email_pattern, context_str):
        # Allow it only if redaction placeholders are used, but to be strictly safe:
        if "[REDACTED" not in context_str:
            logger.error("InsightValidator: Potential raw email detected in context.")
            return False
            
    return True
