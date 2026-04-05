"""Tests for Project 10: Local Copilot."""

import importlib.util
import json
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
    with patch("requests.post"):
        return _load_module(SOLUTION_PATH)


# ── chat ──────────────────────────────────────────────────────


class TestChat:
    """Tests for the chat helper."""

    def test_chat_returns_content(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "completed code"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp):
            result = mod.chat("system", "user msg")
            assert result == "completed code"

    def test_chat_sends_correct_model(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "ok"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp) as mock_post:
            mod.chat("sys", "msg")
            body = mock_post.call_args[1]["json"]
            assert body["model"] == mod.MODEL
            assert body["stream"] is False

    def test_chat_returns_error_string_on_failure(self, mod):
        import requests as real_requests

        with patch.object(
            mod.requests, "post", side_effect=real_requests.ConnectionError("down")
        ):
            result = mod.chat("sys", "msg")
            assert "Error" in result


# ── complete_code ─────────────────────────────────────────────


class TestCompleteCode:
    """Tests for the complete_code function."""

    def test_returns_completion(self, mod):
        with patch.object(mod, "chat", return_value="    return x + y"):
            result = mod.complete_code("def add(x, y):", "python")
            assert result == "    return x + y"

    def test_strips_markdown_fences(self, mod):
        fenced = "```python\n    return x + y\n```"
        with patch.object(mod, "chat", return_value=fenced):
            result = mod.complete_code("def add(x, y):", "python")
            assert "```" not in result
            assert "return x + y" in result

    def test_passes_language_to_prompt(self, mod):
        with patch.object(mod, "chat", return_value="code") as mock_chat:
            mod.complete_code("fn main()", "rust")
            system_arg = mock_chat.call_args[0][0]
            assert "rust" in system_arg.lower()

    def test_empty_completion(self, mod):
        with patch.object(mod, "chat", return_value=""):
            result = mod.complete_code("x = 1", "python")
            assert result == ""


# ── Flask endpoints ───────────────────────────────────────────


class TestFlaskEndpoints:
    """Tests for the Flask endpoints."""

    @pytest.fixture(autouse=True)
    def client(self, mod):
        mod.app.testing = True
        self.client = mod.app.test_client()

    def test_health_endpoint(self, mod):
        resp = self.client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["model"] == mod.MODEL

    def test_complete_endpoint_success(self, mod):
        with patch.object(mod, "complete_code", return_value="    return 42"):
            resp = self.client.post(
                "/complete",
                json={"code": "def answer():", "language": "python"},
                content_type="application/json",
            )
            assert resp.status_code == 200
            data = resp.get_json()
            assert data["completion"] == "    return 42"
            assert data["language"] == "python"

    def test_complete_endpoint_default_language(self, mod):
        with patch.object(mod, "complete_code", return_value="pass") as mock_cc:
            resp = self.client.post(
                "/complete",
                json={"code": "def f():"},
                content_type="application/json",
            )
            assert resp.status_code == 200
            # Default language should be python
            mock_cc.assert_called_once_with("def f():", "python")

    def test_complete_endpoint_missing_code(self, mod):
        resp = self.client.post(
            "/complete",
            json={"language": "python"},
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data
