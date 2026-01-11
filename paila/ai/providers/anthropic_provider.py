"""
Anthropic Provider
==================

Provider for Claude AI models.
"""

import os
from typing import Optional, List

from .base import BaseProvider, Message, AIResponse


class AnthropicProvider(BaseProvider):
    """
    Provider for Anthropic Claude models.

    Usage:
        provider = AnthropicProvider(api_key="sk-...")
        response = provider.chat("Explain this code")
    """

    name = "anthropic"

    # Available models
    MODELS = [
        "claude-opus-4-20250514",
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model to use (default: claude-sonnet-4-20250514)
            **kwargs: Additional options
        """
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment "
                "variable or pass api_key parameter."
            )

        model = model or self.DEFAULT_MODEL

        super().__init__(api_key=api_key, model=model, **kwargs)

        self._client = None

    @property
    def client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install anthropic"
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
        Generate a completion using Claude.

        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            AIResponse with the completion
        """
        # Convert messages to Anthropic format
        system_message = None
        api_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Build request
        request_params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": api_messages,
        }

        if system_message:
            request_params["system"] = system_message

        if temperature != 0.7:  # Only set if not default
            request_params["temperature"] = temperature

        # Add any additional kwargs
        request_params.update(kwargs)

        # Make request
        response = self.client.messages.create(**request_params)

        # Extract content
        content = ""
        if response.content:
            content = response.content[0].text

        return AIResponse(
            content=content,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason or "stop",
        )

    def list_models(self) -> List[str]:
        """
        List available Claude models.

        Returns:
            List of model names
        """
        return self.MODELS.copy()

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Approximate token count
        """
        # Simple approximation: ~4 chars per token for English
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
            "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},
            "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
            "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
            "claude-3-5-haiku-20241022": {"input": 0.8, "output": 4.0},
            "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        }

        model_costs = costs.get(self.model, {"input": 3.0, "output": 15.0})

        input_cost = (input_tokens / 1_000_000) * model_costs["input"]
        output_cost = (output_tokens / 1_000_000) * model_costs["output"]

        return input_cost + output_cost
