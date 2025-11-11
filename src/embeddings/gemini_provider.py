# embeddings/gemini_provider.py
from __future__ import annotations
from typing import List
import os

from .base import EmbeddingProvider, ChatProvider

GEMINI_EMBEDDING_MODEL_DEFAULT = "models/embedding-001"
GEMINI_CHAT_MODEL_DEFAULT = "gemini-2.5-flash-lite"


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Gemini embeddings provider using models/embedding-001."""

    def __init__(self, api_key: str | None = None):
        # Lazy import
        import google.generativeai as genai
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError("Missing GEMINI_API_KEY.")
        genai.configure(api_key=self._api_key)
        self._genai = genai
        model = os.getenv("GEMINI_EMBEDDING_MODEL", GEMINI_EMBEDDING_MODEL_DEFAULT).lower()
        self._model = model

    def embed(self, text: str) -> List[float]:
        result = self._genai.embed_content(
            model=self._model,
            content=text
        )
        # google.generativeai returns {'embedding': [...]} (shape is typically a list[float])
        return result["embedding"]


class GeminiChatProvider(ChatProvider):
    """Gemini chat provider using gemini-2.5-flash-lite."""

    def __init__(self, api_key: str | None = None):
        import google.generativeai as genai
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError("Missing GEMINI_API_KEY.")
        genai.configure(api_key=self._api_key)
        self._genai = genai
        model = os.getenv("GEMINI_CHAT_MODEL") or GEMINI_CHAT_MODEL_DEFAULT
        self._model = genai.GenerativeModel(model)

    def chat(self, messages: list[dict]) -> str:
        """
        For Gemini, we must adapt the OpenAI-like messages array to a single prompt.
        A simple strategy is to concatenate role-tagged contents.
        """
        # Simple formatting to a single string; adapt as needed
        parts: list[str] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append(f"{role.upper()}: {content}")
        prompt = "\n".join(parts)

        res = self._model.generate_content(prompt)
        # Depending on SDK version, check .text / .candidates[0].content parts
        return getattr(res, "text", "") or (res.candidates[0].content.parts[0].text if res.candidates else "")
