"""
Groq Provider
=============

Provider for Groq AI models (ultra-fast inference).
"""

import os
from typing import Optional, List

from .base import BaseProvider, Message, AIResponse


class GroqProvider(BaseProvider):
    """
    Provider for Groq AI models.

    Groq provides ultra-fast inference for open-source models
    like Llama, Mixtral, and Gemma.

    Usage:
        provider = GroqProvider(api_key="gsk_...")
        response = provider.chat("Explain this code")
    """

    name = "groq"

    # Available models
    MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "gemma-7b-it",
    ]

    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Groq provider.

        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Model to use (default: llama-3.3-70b-versatile)
            **kwargs: Additional options
        """
        api_key = api_key or os.environ.get("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "Groq API key required. Set GROQ_API_KEY environment "
                "variable or pass api_key parameter."
            )

        model = model or self.DEFAULT_MODEL

        super().__init__(api_key=api_key, model=model, **kwargs)

        self._client = None

    @property
    def client(self):
        """Lazy-load the Groq client."""
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "groq package required. Install with: pip install groq"
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
        Generate a completion using Groq.

        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            AIResponse with the completion
        """
        # Convert messages to Groq format (OpenAI-compatible)
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
        List available Groq models.

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
            return [m.id for m in models.data]
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
        # Approximate: ~4 chars per token
        return len(text) // 4

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Estimate cost for token usage.

        Groq has very competitive pricing.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        # Approximate costs per 1M tokens (as of 2024)
        # Groq is significantly cheaper than other providers
        costs = {
            "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
            "llama-3.1-70b-versatile": {"input": 0.59, "output": 0.79},
            "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
            "llama3-70b-8192": {"input": 0.59, "output": 0.79},
            "llama3-8b-8192": {"input": 0.05, "output": 0.08},
            "mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
            "gemma2-9b-it": {"input": 0.20, "output": 0.20},
            "gemma-7b-it": {"input": 0.07, "output": 0.07},
        }

        model_costs = costs.get(self.model, {"input": 0.59, "output": 0.79})

        input_cost = (input_tokens / 1_000_000) * model_costs["input"]
        output_cost = (output_tokens / 1_000_000) * model_costs["output"]

        return input_cost + output_cost

    def stream_complete(
        self,
        messages: List[Message],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ):
        """
        Stream a completion from Groq.

        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Yields:
            Content chunks as they arrive
        """
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        request_params = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        request_params.update(kwargs)

        stream = self.client.chat.completions.create(**request_params)

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
