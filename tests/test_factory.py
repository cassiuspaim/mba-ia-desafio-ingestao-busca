# tests/test_factory.py
import os
import importlib
import unittest
from unittest.mock import patch

class TestFactory(unittest.TestCase):
    def setUp(self):
        # Reset environment before each test
        for k in ["AI_PROVIDER", "OPENAI_API_KEY", "GEMINI_API_KEY"]:
            os.environ.pop(k, None)

    def test_openai_selected(self):
        os.environ["AI_PROVIDER"] = "openai"
        os.environ["OPENAI_API_KEY"] = "sk-test"

        # Defer import to after env is set
        factory = importlib.import_module("embeddings.factory")
        with patch("embeddings.openai_provider.OpenAIEmbeddingProvider.__init__", return_value=None), \
             patch("embeddings.openai_provider.OpenAIChatProvider.__init__", return_value=None):
            emb, chat = factory.get_providers()
            self.assertEqual(emb.__class__.__name__, "OpenAIEmbeddingProvider")
            self.assertEqual(chat.__class__.__name__, "OpenAIChatProvider")

    def test_gemini_selected(self):
        os.environ["AI_PROVIDER"] = "gemini"
        os.environ["GEMINI_API_KEY"] = "gm-test"

        factory = importlib.import_module("embeddings.factory")
        with patch("embeddings.gemini_provider.GeminiEmbeddingProvider.__init__", return_value=None), \
             patch("embeddings.gemini_provider.GeminiChatProvider.__init__", return_value=None):
            emb, chat = factory.get_providers()
            self.assertEqual(emb.__class__.__name__, "GeminiEmbeddingProvider")
            self.assertEqual(chat.__class__.__name__, "GeminiChatProvider")

    def test_invalid_provider(self):
        os.environ["AI_PROVIDER"] = "unknown"
        factory = importlib.import_module("embeddings.factory")
        with self.assertRaises(ValueError):
            factory.get_providers()

if __name__ == "__main__":
    unittest.main()
