# embeddings/__init__.py
"""
Embedding and chat provider package.

Contains:
- base: abstract interfaces for EmbeddingProvider and ChatProvider
- openai_provider: OpenAI implementation
- gemini_provider: Gemini implementation
- factory: helper for selecting provider via environment variables
"""
from .base import EmbeddingProvider, ChatProvider
from .factory import get_providers

__all__ = ["EmbeddingProvider", "ChatProvider", "get_providers"]
