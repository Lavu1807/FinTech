"""
Custom exceptions for the LLM Gateway.
"""

class LLMProviderError(Exception):
    """Raised when the LLM provider fails internally."""
    pass

class LLMTimeoutError(Exception):
    """Raised when the LLM request times out."""
    pass

class LLMAuthenticationError(Exception):
    """Raised when authentication with the provider fails."""
    pass

class LLMRateLimitError(Exception):
    """Raised when API rate limits are exceeded."""
    pass
