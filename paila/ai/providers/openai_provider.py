"""
OpenAI Provider
===============

Provider for OpenAI GPT models.
"""

import os
from typing import Optional, List

from .base import BaseProvider, Message, AIResponse


class OpenAIProvider(BaseProvider):
    """
    Provider for OpenAI GPT models.

    Usage:
        provider = OpenAIProvider(api_key="sk-...")
        response = provider.chat("Explain this code")
    """

    name = "openai"

    # Available models
    MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
    ]

    DEFAULT_MODEL = "gpt-4o"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        organization: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o)
            organization: Organization ID (optional)
            **kwargs: Additional options
        """
        api_key = api_key or os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment "
                "variable or pass api_key parameter."
            )

        model = model or self.DEFAULT_MODEL

        super().__init__(api_key=api_key, model=model, **kwargs)

        self.organization = organization
        self._client = None

    @property
    def client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            try:
                import openai

                client_kwargs = {"api_key": self.api_key}
                if self.organization:
                    client_kwargs["organization"] = self.organization

                self._client = openai.OpenAI(**client_kwargs)
            except ImportError:
                raise ImportError(
                    "openai package required. Install with: pip install openai"
                )
        return self._client

    def complete(
        self,
        messages: List[Message],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Generate a completion using GPT.

        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            AIResponse with the completion
        """
        # Convert messages to OpenAI format
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Build request
        request_params = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # Add any additional kwargs
        request_params.update(kwargs)

        # Make request
        response = self.client.chat.completions.create(**request_params)

        # Extract content
        content = ""
        if response.choices:
            content = response.choices[0].message.content or ""

        return AIResponse(
            content=content,
            model=response.model,
            usage={
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
            },
            finish_reason=response.choices[0].finish_reason if response.choices else "stop",
        )

    def list_models(self) -> List[str]:
        """
        List available GPT models.

        Returns:
            List of model names
        """
        return self.MODELS.copy()

    def get_available_models(self) -> List[str]:
        """
        Fetch available models from API.

        Returns:
            List of model IDs
        """
        try:
            models = self.client.models.list()
            return [m.id for m in models.data if "gpt" in m.id.lower()]
        except Exception:
            return self.MODELS.copy()

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Approximate token count
        """
        # Try using tiktoken if available
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except (ImportError, KeyError):
            # Fallback: ~4 chars per token
            return len(text) // 4

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Estimate cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        # Approximate costs per 1M tokens (as of 2024)
        costs = {
            "gpt-4o": {"input": 5.0, "output": 15.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "gpt-3.5-turbo-16k": {"input": 1.0, "output": 2.0},
        }

        model_costs = costs.get(self.model, {"input": 5.0, "output": 15.0})

        input_cost = (input_tokens / 1_000_000) * model_costs["input"]
        output_cost = (output_tokens / 1_000_000) * model_costs["output"]

        return input_cost + output_cost

    def create_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """
        Create embedding for text.

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
