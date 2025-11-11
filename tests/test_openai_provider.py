# tests/test_openai_provider.py
import os
import unittest
from unittest.mock import patch, MagicMock

from embeddings.openai_provider import (
    OpenAIEmbeddingProvider,
    OpenAIChatProvider,
    OPENAI_EMBEDDING_MODEL_DEFAULT,
    OPENAI_CHAT_MODEL_DEFAULT
)


class TestOpenAIProvider(unittest.TestCase):
    def setUp(self):
        os.environ["OPENAI_API_KEY"] = "sk-test"
        # Clear model env vars to test defaults
        os.environ.pop("OPENAI_EMBEDDING_MODEL", None)
        os.environ.pop("OPENAI_CHAT_MODEL", None)

    @patch("embeddings.openai_provider.OpenAIEmbeddingProvider.__init__", return_value=None)
    def test_embed_shape_default_model(self, _):
        provider = OpenAIEmbeddingProvider.__new__(OpenAIEmbeddingProvider)
        provider._api_key = "sk-test"
        provider._model = OPENAI_EMBEDDING_MODEL_DEFAULT

        # Mock OpenAI client and response
        fake_client = MagicMock()
        provider._client = fake_client
        fake_resp = MagicMock()
        fake_resp.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        fake_client.embeddings.create.return_value = fake_resp

        vec = provider.embed("hello")
        self.assertEqual(vec, [0.1, 0.2, 0.3])
        fake_client.embeddings.create.assert_called_once_with(
            model=OPENAI_EMBEDDING_MODEL_DEFAULT,
            input="hello"
        )

    @patch("embeddings.openai_provider.OpenAIEmbeddingProvider.__init__", return_value=None)
    def test_embed_shape_custom_model(self, _):
        # Test with custom model from environment variable
        os.environ["OPENAI_EMBEDDING_MODEL"] = "custom-embedding-model"
        
        provider = OpenAIEmbeddingProvider.__new__(OpenAIEmbeddingProvider)
        provider._api_key = "sk-test"
        provider._model = "custom-embedding-model"  # Simulate what __init__ would set

        fake_client = MagicMock()
        provider._client = fake_client
        fake_resp = MagicMock()
        fake_resp.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        fake_client.embeddings.create.return_value = fake_resp

        vec = provider.embed("hello")
        self.assertEqual(vec, [0.1, 0.2, 0.3])
        fake_client.embeddings.create.assert_called_once_with(
            model="custom-embedding-model",
            input="hello"
        )

    @patch("embeddings.openai_provider.OpenAIChatProvider.__init__", return_value=None)
    def test_chat_return_default_model(self, _):
        provider = OpenAIChatProvider.__new__(OpenAIChatProvider)
        provider._api_key = "sk-test"
        provider._model = OPENAI_CHAT_MODEL_DEFAULT
        fake_client = MagicMock()
        provider._client = fake_client

        fake_choice = MagicMock()
        fake_choice.message.content = "ok"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client.chat.completions.create.return_value = fake_resp

        out = provider.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(out, "ok")
        fake_client.chat.completions.create.assert_called_once()
        args, kwargs = fake_client.chat.completions.create.call_args
        self.assertEqual(kwargs["model"], OPENAI_CHAT_MODEL_DEFAULT)

    @patch("embeddings.openai_provider.OpenAIChatProvider.__init__", return_value=None)
    def test_chat_return_custom_model(self, _):
        # Test with custom model from environment variable
        os.environ["OPENAI_CHAT_MODEL"] = "custom-chat-model"
        
        provider = OpenAIChatProvider.__new__(OpenAIChatProvider)
        provider._api_key = "sk-test"
        provider._model = "custom-chat-model"  # Simulate what __init__ would set
        fake_client = MagicMock()
        provider._client = fake_client

        fake_choice = MagicMock()
        fake_choice.message.content = "ok"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client.chat.completions.create.return_value = fake_resp

        out = provider.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(out, "ok")
        fake_client.chat.completions.create.assert_called_once()
        args, kwargs = fake_client.chat.completions.create.call_args
        self.assertEqual(kwargs["model"], "custom-chat-model")


if __name__ == "__main__":
    unittest.main()
