"""Tests for Project 01: AI Chatbot."""

import importlib.util
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "reference", "main.py"
)


def _load_module(path: str):
    spec = importlib.util.spec_from_file_location("student_main", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "Hello!"}}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp
        module = _load_module(SOLUTION_PATH)
    return module


# ---- Tests ----


class TestChat:
    """Tests for the chat() function."""

    def test_chat_returns_string(self, mod):
        """chat() should return the assistant's reply as a string."""
        mod.history.clear()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "message": {"content": "I am a helpful assistant."}
            }
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.chat("Hello")
            assert isinstance(result, str)
            assert result == "I am a helpful assistant."

    def test_chat_appends_user_message_to_history(self, mod):
        """chat() should add the user's message to history."""
        mod.history.clear()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "Reply"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            mod.chat("Test message")
            assert any(
                m["role"] == "user" and m["content"] == "Test message"
                for m in mod.history
            )

    def test_chat_appends_assistant_reply_to_history(self, mod):
        """chat() should add the assistant's reply to history."""
        mod.history.clear()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "Bot reply"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            mod.chat("Hi")
            assert any(
                m["role"] == "assistant" and m["content"] == "Bot reply"
                for m in mod.history
            )

    def test_chat_sends_correct_payload(self, mod):
        """chat() should POST to Ollama with the correct model and messages."""
        mod.history.clear()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "ok"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            mod.chat("ping")

            call_kwargs = mock_post.call_args
            payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs.kwargs["json"]
            assert payload["model"] == mod.MODEL
            assert payload["stream"] is False
            assert any(m["content"] == "ping" for m in payload["messages"])

    def test_chat_multi_turn_history_grows(self, mod):
        """History should accumulate across multiple chat() calls."""
        mod.history.clear()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "r1"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            mod.chat("first")
            mod.chat("second")

            # 2 user + 2 assistant = 4 messages
            assert len(mod.history) == 4

    def test_chat_raises_on_http_error(self, mod):
        """chat() should propagate HTTP errors via raise_for_status."""
        mod.history.clear()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.side_effect = Exception("500 Server Error")
            mock_post.return_value = mock_resp

            with pytest.raises(Exception, match="500 Server Error"):
                mod.chat("fail")


class TestModuleConstants:
    """Tests for module-level constants and setup."""

    def test_ollama_url_defined(self, mod):
        assert hasattr(mod, "OLLAMA_URL")
        assert "11434" in mod.OLLAMA_URL

    def test_model_defined(self, mod):
        assert hasattr(mod, "MODEL")
        assert isinstance(mod.MODEL, str)
        assert len(mod.MODEL) > 0
