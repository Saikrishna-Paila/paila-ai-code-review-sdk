"""
Base AI Provider
================

Abstract base class for AI providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class Message:
    """A single message in a conversation."""
    role: str  # "user", "assistant", or "system"
    content: str


@dataclass
class AIResponse:
    """Response from an AI model."""
    content: str
    model: str
    usage: Dict[str, int]  # tokens used
    finish_reason: str = "stop"


class BaseProvider(ABC):
    """
    Abstract base class for AI providers.

    To create a custom provider:

        class MyProvider(BaseProvider):
            name = "my_provider"

            def complete(self, messages, **kwargs):
                # Call your AI API
                return AIResponse(...)
    """

    name: str = "base"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the provider.

        Args:
            api_key: API key for authentication
            model: Default model to use
            **kwargs: Additional provider-specific options
        """
        self.api_key = api_key
        self.model = model
        self.options = kwargs

    @abstractmethod
    def complete(
        self,
        messages: List[Message],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Generate a completion from messages.

        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            AIResponse with the completion
        """
        pass

    def chat(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple chat interface.

        Args:
            prompt: User prompt
            system: System message (optional)
            **kwargs: Additional parameters

        Returns:
            Response text
        """
        messages = []

        if system:
            messages.append(Message(role="system", content=system))

        messages.append(Message(role="user", content=prompt))

        response = self.complete(messages, **kwargs)
        return response.content

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models.

        Returns:
            List of model names
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.model}')"
