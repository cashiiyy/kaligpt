"""Tests for Ollama provider and local OpenAI-compatible server support."""

from unittest import mock
from types import SimpleNamespace
from agents.utils.agent_configs import get_default_model, get_default_provider, get_ai_specific_default_model, get_api_key
from agents.ollama import OpenAICompatClient


def test_default_config_is_qwen():
    assert get_default_model() == "qwen3.5-9b-uncensored-hauhaucs-aggressive"
    assert get_default_provider() == "ollama"
    assert get_ai_specific_default_model("ollama") == "qwen3.5-9b-uncensored-hauhaucs-aggressive"
    assert get_api_key("ollama") == "http://localhost:1234"


def test_openai_compat_client_chat():
    with mock.patch("openai.OpenAI") as mock_openai_cls:
        mock_instance = mock.MagicMock()
        mock_openai_cls.return_value = mock_instance

        fake_choice = SimpleNamespace(
            message=SimpleNamespace(
                content="test response",
                reasoning_content="thinking steps",
                tool_calls=[]
            )
        )
        mock_instance.chat.completions.create.return_value = SimpleNamespace(choices=[fake_choice])

        client = OpenAICompatClient(host="http://localhost:1234")
        resp = client.chat(
            model="qwen3.5-9b-uncensored-hauhaucs-aggressive",
            messages=[{"role": "user", "content": "hi"}]
        )

        assert "> [Thinking]" in resp.message.content
        assert "test response" in resp.message.content
        mock_instance.chat.completions.create.assert_called_once()
