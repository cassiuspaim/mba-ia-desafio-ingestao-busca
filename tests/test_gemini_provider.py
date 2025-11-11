# tests/test_gemini_provider.py
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

from embeddings.gemini_provider import (
    GeminiEmbeddingProvider,
    GeminiChatProvider,
    GEMINI_EMBEDDING_MODEL_DEFAULT,
    GEMINI_CHAT_MODEL_DEFAULT
)


class TestGeminiProvider(unittest.TestCase):
    def setUp(self):
        os.environ["GEMINI_API_KEY"] = "gm-test"
        # Clear model env vars to test defaults
        os.environ.pop("GEMINI_EMBEDDING_MODEL", None)
        os.environ.pop("GEMINI_CHAT_MODEL", None)

    def test_embed_shape_default_model(self):
        # Mock google.generativeai module before importing the provider
        mock_genai = MagicMock()
        mock_genai.embed_content.return_value = {"embedding": [0.9, 0.8]}
        
        # Remove from cache if already imported
        if "google.generativeai" in sys.modules:
            del sys.modules["google.generativeai"]
        if "embeddings.gemini_provider" in sys.modules:
            del sys.modules["embeddings.gemini_provider"]
        
        # Patch sys.modules to inject the mock before the import happens
        with patch.dict(sys.modules, {"google.generativeai": mock_genai}):
            # Import here so it uses the mocked module
            from embeddings.gemini_provider import GeminiEmbeddingProvider, GEMINI_EMBEDDING_MODEL_DEFAULT
            
            provider = GeminiEmbeddingProvider(api_key="gm-test")
            vec = provider.embed("hello")
            self.assertEqual(vec, [0.9, 0.8])
            mock_genai.embed_content.assert_called_once_with(
                model=GEMINI_EMBEDDING_MODEL_DEFAULT.lower(),
                content="hello"
            )

    def test_embed_shape_custom_model(self):
        # Test with custom model from environment variable
        os.environ["GEMINI_EMBEDDING_MODEL"] = "custom-embedding-model"
        
        mock_genai = MagicMock()
        mock_genai.embed_content.return_value = {"embedding": [0.9, 0.8]}
        
        if "google.generativeai" in sys.modules:
            del sys.modules["google.generativeai"]
        if "embeddings.gemini_provider" in sys.modules:
            del sys.modules["embeddings.gemini_provider"]
        
        with patch.dict(sys.modules, {"google.generativeai": mock_genai}):
            from embeddings.gemini_provider import GeminiEmbeddingProvider
            
            provider = GeminiEmbeddingProvider(api_key="gm-test")
            vec = provider.embed("hello")
            self.assertEqual(vec, [0.9, 0.8])
            mock_genai.embed_content.assert_called_once_with(
                model="custom-embedding-model".lower(),
                content="hello"
            )

    def test_chat_return_default_model(self):
        # Mock google.generativeai module before importing the provider
        mock_genai = MagicMock()
        fake_model = MagicMock()
        mock_genai.GenerativeModel.return_value = fake_model
        fake_res = MagicMock()
        fake_res.text = "answer"
        fake_model.generate_content.return_value = fake_res
        
        # Remove from cache if already imported
        if "google.generativeai" in sys.modules:
            del sys.modules["google.generativeai"]
        if "embeddings.gemini_provider" in sys.modules:
            del sys.modules["embeddings.gemini_provider"]
        
        # Patch sys.modules to inject the mock before the import happens
        with patch.dict(sys.modules, {"google.generativeai": mock_genai}):
            # Import here so it uses the mocked module
            from embeddings.gemini_provider import GeminiChatProvider, GEMINI_CHAT_MODEL_DEFAULT
            
            provider = GeminiChatProvider(api_key="gm-test")
            out = provider.chat([{"role": "user", "content": "hi"}])
            self.assertEqual(out, "answer")
            mock_genai.GenerativeModel.assert_called_once_with(GEMINI_CHAT_MODEL_DEFAULT)
            fake_model.generate_content.assert_called_once()

    def test_chat_return_custom_model(self):
        # Test with custom model from environment variable
        os.environ["GEMINI_CHAT_MODEL"] = "custom-chat-model"
        
        mock_genai = MagicMock()
        fake_model = MagicMock()
        mock_genai.GenerativeModel.return_value = fake_model
        fake_res = MagicMock()
        fake_res.text = "answer"
        fake_model.generate_content.return_value = fake_res
        
        if "google.generativeai" in sys.modules:
            del sys.modules["google.generativeai"]
        if "embeddings.gemini_provider" in sys.modules:
            del sys.modules["embeddings.gemini_provider"]
        
        with patch.dict(sys.modules, {"google.generativeai": mock_genai}):
            from embeddings.gemini_provider import GeminiChatProvider
            
            provider = GeminiChatProvider(api_key="gm-test")
            out = provider.chat([{"role": "user", "content": "hi"}])
            self.assertEqual(out, "answer")
            mock_genai.GenerativeModel.assert_called_once_with("custom-chat-model")
            fake_model.generate_content.assert_called_once()


if __name__ == "__main__":
    unittest.main()
