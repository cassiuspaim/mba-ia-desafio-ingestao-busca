# embeddings/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Protocol


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Return a single embedding vector for the given text."""
        pass

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        """Default batch implementation; providers may override for efficiency."""
        return [self.embed(t) for t in texts]


class ChatProvider(ABC):
    """Abstract base class for chat/LLM providers."""

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        """
        Execute a chat completion and return the assistant's content.
        messages example: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        pass
