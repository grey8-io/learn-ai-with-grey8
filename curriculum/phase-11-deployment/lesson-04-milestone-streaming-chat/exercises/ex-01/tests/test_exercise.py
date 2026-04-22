"""Tests for Project 08: Streaming Chat App."""

import importlib.util
import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "solution", "main.py"
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
        mock_resp.json.return_value = {"message": {"content": "ok"}}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp
        module = _load_module(SOLUTION_PATH)
    return module


@pytest.fixture()
def client(mod):
    """Create a FastAPI test client."""
    from fastapi.testclient import TestClient
    return TestClient(mod.app)


# ---- Tests ----


class TestChatRequestModel:
    """Tests for the ChatRequest Pydantic model."""

    def test_chat_request_valid(self, mod):
        req = mod.ChatRequest(message="Hello")
        assert req.message == "Hello"

    def test_chat_request_requires_message(self, mod):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            mod.ChatRequest()


class TestStreamChat:
    """Tests for stream_chat() generator."""

    def test_stream_chat_yields_tokens(self, mod):
        """stream_chat() should yield dicts with 'data' key for each token."""
        lines = [
            json.dumps({"message": {"content": "Hello"}, "done": False}).encode(),
            json.dumps({"message": {"content": " world"}, "done": False}).encode(),
            json.dumps({"message": {"content": ""}, "done": True}).encode(),
        ]

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.iter_lines.return_value = lines
            mock_post.return_value = mock_resp

            tokens = list(mod.stream_chat("Hi"))
            # Should yield for non-empty tokens
            assert len(tokens) == 2
            assert tokens[0] == {"data": "Hello"}
            assert tokens[1] == {"data": " world"}

    def test_stream_chat_stops_on_done(self, mod):
        """stream_chat() should stop iterating when done=True."""
        lines = [
            json.dumps({"message": {"content": "First"}, "done": False}).encode(),
            json.dumps({"message": {"content": ""}, "done": True}).encode(),
            json.dumps({"message": {"content": "Ignored"}, "done": False}).encode(),
        ]

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.iter_lines.return_value = lines
            mock_post.return_value = mock_resp

            tokens = list(mod.stream_chat("test"))
            # Should only get "First", not "Ignored"
            assert len(tokens) == 1
            assert tokens[0] == {"data": "First"}

    def test_stream_chat_sends_stream_true(self, mod):
        """stream_chat() should request streaming from Ollama."""
        lines = [
            json.dumps({"message": {"content": ""}, "done": True}).encode(),
        ]

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.iter_lines.return_value = lines
            mock_post.return_value = mock_resp

            list(mod.stream_chat("hi"))

            call_kwargs = mock_post.call_args
            payload = call_kwargs[1]["json"]
            assert payload["stream"] is True

    def test_stream_chat_includes_system_prompt(self, mod):
        """stream_chat() should include a system message in the request."""
        lines = [
            json.dumps({"message": {"content": ""}, "done": True}).encode(),
        ]

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.iter_lines.return_value = lines
            mock_post.return_value = mock_resp

            list(mod.stream_chat("hello"))

            payload = mock_post.call_args[1]["json"]
            messages = payload["messages"]
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "hello"


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "model" in data


class TestIndexEndpoint:
    """Tests for GET / (HTML page)."""

    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "Streaming Chat" in resp.text

    def test_index_contains_chat_ui_elements(self, client):
        """The HTML page should contain the chat interface elements."""
        resp = client.get("/")
        html = resp.text
        assert "chat-box" in html
        assert "user-input" in html
        assert "sendMessage" in html


class TestChatEndpoint:
    """Tests for POST /chat SSE endpoint."""

    def test_chat_endpoint_returns_sse(self, mod, client):
        """POST /chat should return a streaming response."""
        lines = [
            json.dumps({"message": {"content": "Hi"}, "done": False}).encode(),
            json.dumps({"message": {"content": ""}, "done": True}).encode(),
        ]

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.iter_lines.return_value = lines
            mock_post.return_value = mock_resp

            resp = client.post("/chat", json={"message": "Hello"})
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")
