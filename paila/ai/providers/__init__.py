"""
AI Providers for Paila SDK
==========================

Supported AI model providers for code review enhancement.
"""

from .base import BaseProvider
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider
from .groq_provider import GroqProvider

__all__ = [
    "BaseProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "GroqProvider",
]


def get_provider(name: str, **kwargs) -> BaseProvider:
    """
    Get AI provider by name.

    Args:
        name: Provider name ("anthropic", "openai", or "groq")
        **kwargs: Provider-specific arguments

    Returns:
        Configured provider instance
    """
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "groq": GroqProvider,
    }

    if name not in providers:
        raise ValueError(f"Unknown provider: {name}. Available: {list(providers.keys())}")

    return providers[name](**kwargs)
