# embeddings/factory.py
from __future__ import annotations
import os
from typing import Tuple

from .base import EmbeddingProvider, ChatProvider
from .openai_provider import OpenAIEmbeddingProvider, OpenAIChatProvider
from .gemini_provider import GeminiEmbeddingProvider, GeminiChatProvider


def get_providers() -> Tuple[EmbeddingProvider, ChatProvider]:
    """
    Decide providers via ENV:
      AI_PROVIDER = "openai" | "gemini"
      OPENAI_API_KEY / GEMINI_API_KEY must be set accordingly.
    """
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    if provider == "openai":
        return OpenAIEmbeddingProvider(), OpenAIChatProvider()
    elif provider == "gemini":
        return GeminiEmbeddingProvider(), GeminiChatProvider()
    raise ValueError(f"Unknown AI_PROVIDER: {provider}")
