"""
Reusable schemas for the LLM Gateway.
"""

from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class GatewayResponse(BaseModel):
    """Standard text generation response wrapper."""

    content: str = Field(description="The generated text from the LLM.")
    execution_time: float = Field(
        description="Time taken to execute the request in seconds."
    )
    provider: str = Field(description="The name of the LLM provider used.")
    estimated_tokens: int = Field(default=0, description="Estimated total tokens used.")
    estimated_cost: float = Field(default=0.0, description="Estimated cost in USD.")


class StructuredGatewayResponse(BaseModel, Generic[T]):
    """Structured data generation response wrapper."""

    data: T = Field(description="The structured Pydantic object returned by the LLM.")
    execution_time: float = Field(
        description="Time taken to execute the request in seconds."
    )
    provider: str = Field(description="The name of the LLM provider used.")
    estimated_tokens: int = Field(default=0, description="Estimated total tokens used.")
    estimated_cost: float = Field(default=0.0, description="Estimated cost in USD.")
