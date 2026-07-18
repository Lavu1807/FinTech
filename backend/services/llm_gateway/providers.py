"""
Provider abstractions for the LLM Gateway.
"""

from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Any, Dict
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """
    Abstract base class defining the contract for all LLM providers.
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the internal name of the provider."""
        pass

    @abstractmethod
    def invoke(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """Standard text invocation."""
        pass

    @abstractmethod
    def invoke_structured(
        self,
        prompt: str,
        output_schema: Type[T],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> T:
        """Structured invocation."""
        pass





class MistralProvider(BaseLLMProvider):
    """
    Concrete implementation of the Mistral LLM provider.
    """

    def __init__(self, api_key: str, model_name: str = "mistral-large-latest"):
        from langchain_mistralai import ChatMistralAI

        self.model_name = model_name
        self._base_llm = ChatMistralAI(
            model=model_name, mistral_api_key=api_key, max_retries=0
        )

    def get_provider_name(self) -> str:
        return f"Mistral ({self.model_name})"

    def _get_configured_llm(
        self, temperature: float, max_tokens: Optional[int], timeout: Optional[int]
    ) -> BaseChatModel:
        bind_kwargs: Dict[str, Any] = {"temperature": temperature}
        if max_tokens is not None:
            bind_kwargs["max_tokens"] = max_tokens
        if timeout is not None:
            bind_kwargs["timeout"] = timeout
        return self._base_llm.bind(**bind_kwargs)

    def invoke(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> str:
        configured_llm = self._get_configured_llm(temperature, max_tokens, timeout)
        response = configured_llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)

    def invoke_structured(
        self,
        prompt: str,
        output_schema: Type[T],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> T:
        configured_llm = self._get_configured_llm(temperature, max_tokens, timeout)
        structured_llm = configured_llm.with_structured_output(output_schema)
        return structured_llm.invoke(prompt)


class OpenAIProvider(BaseLLMProvider):
    def get_provider_name(self) -> str:
        return "OpenAI"

    def invoke(self, *args, **kwargs):
        raise NotImplementedError("OpenAI provider not yet implemented.")

    def invoke_structured(self, *args, **kwargs):
        raise NotImplementedError("OpenAI provider not yet implemented.")


class ClaudeProvider(BaseLLMProvider):
    def get_provider_name(self) -> str:
        return "Claude"

    def invoke(self, *args, **kwargs):
        raise NotImplementedError("Claude provider not yet implemented.")

    def invoke_structured(self, *args, **kwargs):
        raise NotImplementedError("Claude provider not yet implemented.")


class GroqProvider(BaseLLMProvider):
    def get_provider_name(self) -> str:
        return "Groq"

    def invoke(self, *args, **kwargs):
        raise NotImplementedError("Groq provider not yet implemented.")

    def invoke_structured(self, *args, **kwargs):
        raise NotImplementedError("Groq provider not yet implemented.")


class ProviderFactory:
    """Factory to instantiate the requested LLM provider."""

    @staticmethod
    def create_provider(provider_name: str, api_key: str) -> BaseLLMProvider:
        name = provider_name.lower()
        if name == "mistral":
            return MistralProvider(api_key=api_key)
        elif name == "openai":
            return OpenAIProvider()
        elif name == "claude":
            return ClaudeProvider()
        elif name == "groq":
            return GroqProvider()
        else:
            raise ValueError(f"Unknown provider requested: {provider_name}")
