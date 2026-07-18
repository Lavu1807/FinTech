"""
Centralized LLM Gateway Implementation.
"""

import time
from typing import Type, TypeVar, Optional, Any

from pydantic import BaseModel

from backend.config.settings import settings
from backend.utils.logger import logger
from .providers import BaseLLMProvider, ProviderFactory
from .exceptions import LLMProviderError, LLMAuthenticationError
from .schemas import GatewayResponse, StructuredGatewayResponse

T = TypeVar("T", bound=BaseModel)


class LLMGateway:
    """
    Singleton service for centralized LLM interactions.
    """

    _instance = None
    _provider: BaseLLMProvider = None

    def __new__(cls):
        """Ensures only a single instance of LLMGateway exists."""
        if cls._instance is None:
            cls._instance = super(LLMGateway, cls).__new__(cls)
            cls._instance._initialize_provider()
        return cls._instance

    def _initialize_provider(self) -> None:
        """
        Initializes the underlying LLM provider from settings.
        """
        provider_name = getattr(settings, "LLM_PROVIDER", "mistral").lower()

        if provider_name == "mistral":
            if not settings.MISTRAL_API_KEY:
                logger.error(
                    "MISTRAL_API_KEY is missing. LLM Gateway cannot authenticate."
                )
                raise LLMAuthenticationError("Missing Mistral API key in settings.")
            api_key = (
                settings.MISTRAL_API_KEY.get_secret_value()
                if hasattr(settings.MISTRAL_API_KEY, "get_secret_value")
                else settings.MISTRAL_API_KEY
            )
        else:
            api_key = None

        self._provider = ProviderFactory.create_provider(provider_name, api_key=api_key)
        logger.info(
            f"LLMGateway: Initialized provider {self._provider.get_provider_name()}"
        )

    def _execute_with_retries(self, func, *args, max_retries: int = 3, **kwargs) -> Any:
        """
        Executes an LLM call with exponential backoff for transient errors.
        """
        attempt = 0
        while attempt < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e).lower()

                # Do not retry fatal client errors (400)
                if "invalid" in error_msg or "400" in error_msg:
                    logger.error(f"LLMGateway: Invalid request format: {str(e)}")
                    raise LLMProviderError(f"Invalid LLM request: {str(e)}") from e

                attempt += 1
                logger.warning(
                    f"LLMGateway: Transient error on attempt {attempt}/{max_retries}: {str(e)}"
                )

                if attempt >= max_retries:
                    raise LLMProviderError(
                        f"LLM failed after {max_retries} attempts due to: {str(e)}"
                    ) from e

                time.sleep(2**attempt)

    def invoke(
        self,
        prompt: str,
        calling_agent: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> GatewayResponse:
        """
        Standard text generation invocation.
        """
        start_time = time.time()

        def _call():
            return self._provider.invoke(prompt, temperature, max_tokens, timeout)

        try:
            result = self._execute_with_retries(_call)
            exec_time = time.time() - start_time

            # Simple heuristic for token estimate: 4 chars ~ 1 token
            est_tokens = len(prompt) // 4 + len(str(result)) // 4
            est_cost = (est_tokens / 1000) * 0.00015  # Flash pricing approx

            logger.info(
                f"LLMGateway | Agent: {calling_agent} | Type: Standard | Status: SUCCESS | Time: {exec_time:.2f}s | Tokens: ~{est_tokens}"
            )
            return GatewayResponse(
                content=result,
                execution_time=exec_time,
                provider=self._provider.get_provider_name(),
                estimated_tokens=est_tokens,
                estimated_cost=est_cost,
            )
        except Exception as e:
            exec_time = time.time() - start_time
            logger.error(
                f"LLMGateway | Agent: {calling_agent} | Type: Standard | Status: FAILED | Time: {exec_time:.2f}s | Error: {str(e)}"
            )
            raise

    def invoke_structured(
        self,
        prompt: str,
        output_schema: Type[T],
        calling_agent: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> StructuredGatewayResponse[T]:
        """
        Structured data generation invocation.
        """
        start_time = time.time()

        def _call():
            return self._provider.invoke_structured(
                prompt, output_schema, temperature, max_tokens, timeout
            )

        try:
            result = self._execute_with_retries(_call)
            exec_time = time.time() - start_time

            est_tokens = len(prompt) // 4 + len(str(result.model_dump())) // 4
            est_cost = (est_tokens / 1000) * 0.00015

            logger.info(
                f"LLMGateway | Agent: {calling_agent} | Type: Structured | Status: SUCCESS | Time: {exec_time:.2f}s | Tokens: ~{est_tokens}"
            )
            return StructuredGatewayResponse(
                data=result,
                execution_time=exec_time,
                provider=self._provider.get_provider_name(),
                estimated_tokens=est_tokens,
                estimated_cost=est_cost,
            )
        except Exception as e:
            exec_time = time.time() - start_time
            logger.error(
                f"LLMGateway | Agent: {calling_agent} | Type: Structured | Status: FAILED | Time: {exec_time:.2f}s | Error: {str(e)}"
            )
            raise


# Global singleton instance
llm_gateway = LLMGateway()
