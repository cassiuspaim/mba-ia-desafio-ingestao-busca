# embeddings/openai_provider.py
from __future__ import annotations
from typing import List
import os

from .base import EmbeddingProvider, ChatProvider

OPENAI_EMBEDDING_MODEL_DEFAULT = "text-embedding-3-small"
OPENAI_CHAT_MODEL_DEFAULT = "gpt-5-nano"


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embeddings provider using text-embedding-3-small."""

    def __init__(self, api_key: str | None = None):
        # Lazy import to avoid hard dependency if not used
        from openai import OpenAI
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("Missing OPENAI_API_KEY.")
        self._client = OpenAI(api_key=self._api_key)
        model = os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL_DEFAULT)
        self._model = model

    def embed(self, text: str) -> List[float]:
        # NOTE: response schema depends on openai client version
        resp = self._client.embeddings.create(
            model=self._model,
            input=text
        )
        return resp.data[0].embedding


class OpenAIChatProvider(ChatProvider):
    """OpenAI chat provider using gpt-5-nano."""

    def __init__(self, api_key: str | None = None):
        from openai import OpenAI
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("Missing OPENAI_API_KEY.")
        self._client = OpenAI(api_key=self._api_key)
        model = os.getenv("OPENAI_CHAT_MODEL") or OPENAI_CHAT_MODEL_DEFAULT
        self._model = model

    def chat(self, messages: list[dict]) -> str:
        # Depending on SDK version, could be .chat.completions.create or .responses.create
        # Here we use chat.completions for clarity.
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content
