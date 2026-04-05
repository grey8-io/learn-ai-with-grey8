"""Tests for Project 09: AI Content Moderator."""

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


# ── extract_json ──────────────────────────────────────────────


class TestExtractJson:
    """Tests for the extract_json helper."""

    def test_plain_json(self, mod):
        raw = '{"category": "safe", "severity": 1, "explanation": "ok"}'
        result = mod.extract_json(raw)
        assert result["category"] == "safe"
        assert result["severity"] == 1

    def test_json_inside_code_fences(self, mod):
        raw = '```json\n{"category": "unsafe", "severity": 5, "explanation": "bad"}\n```'
        result = mod.extract_json(raw)
        assert result["category"] == "unsafe"
        assert result["severity"] == 5

    def test_json_inside_plain_fences(self, mod):
        raw = '```\n{"category": "warning", "severity": 3, "explanation": "hmm"}\n```'
        result = mod.extract_json(raw)
        assert result["category"] == "warning"

    def test_invalid_json_raises(self, mod):
        with pytest.raises(json.JSONDecodeError):
            mod.extract_json("not json at all")


# ── chat ──────────────────────────────────────────────────────


class TestChat:
    """Tests for the chat helper."""

    def test_chat_returns_content(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "hello"}}
        mock_resp.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_resp) as mock_post:
            # Patch at the module level
            original = mod.requests.post
            mod.requests.post = mock_post
            try:
                result = mod.chat("system prompt", "user message")
                assert result == "hello"
                mock_post.assert_called_once()
                call_kwargs = mock_post.call_args
                body = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][1]
                assert body["model"] == mod.MODEL
            finally:
                mod.requests.post = original

    def test_chat_raises_http_exception_on_connection_error(self, mod):
        import requests as real_requests

        with patch.object(
            mod.requests, "post", side_effect=real_requests.ConnectionError("down")
        ):
            with pytest.raises(Exception):
                mod.chat("sys", "msg")


# ── moderate ──────────────────────────────────────────────────


class TestModerate:
    """Tests for the moderate function."""

    def test_moderate_safe_text(self, mod):
        llm_response = '{"category": "safe", "severity": 1, "explanation": "Normal text"}'
        with patch.object(mod, "chat", return_value=llm_response):
            result = mod.moderate("Hello, how are you?")
            assert result.category == "safe"
            assert result.severity == 1
            assert result.explanation == "Normal text"

    def test_moderate_unsafe_text(self, mod):
        llm_response = '{"category": "unsafe", "severity": 5, "explanation": "Threatening"}'
        with patch.object(mod, "chat", return_value=llm_response):
            result = mod.moderate("some bad text")
            assert result.category == "unsafe"
            assert result.severity == 5

    def test_moderate_clamps_severity(self, mod):
        llm_response = '{"category": "safe", "severity": 99, "explanation": "Over"}'
        with patch.object(mod, "chat", return_value=llm_response):
            result = mod.moderate("test")
            assert result.severity == 5

    def test_moderate_clamps_severity_low(self, mod):
        llm_response = '{"category": "safe", "severity": -2, "explanation": "Under"}'
        with patch.object(mod, "chat", return_value=llm_response):
            result = mod.moderate("test")
            assert result.severity == 1

    def test_moderate_normalizes_unknown_category(self, mod):
        llm_response = '{"category": "UNKNOWN", "severity": 3, "explanation": "?"}'
        with patch.object(mod, "chat", return_value=llm_response):
            result = mod.moderate("test")
            assert result.category == "warning"

    def test_moderate_fallback_on_invalid_json(self, mod):
        with patch.object(mod, "chat", return_value="totally not json"):
            result = mod.moderate("test")
            assert result.category == "warning"
            assert result.severity == 3
            assert "Could not parse" in result.explanation


# ── FastAPI endpoints (via TestClient) ────────────────────────


class TestEndpoints:
    """Tests for the FastAPI endpoints."""

    @pytest.fixture(autouse=True)
    def client(self, mod):
        from fastapi.testclient import TestClient
        self.client = TestClient(mod.app)

    def test_health(self, mod):
        resp = self.client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "model" in data

    def test_moderate_endpoint(self, mod):
        llm_resp = '{"category": "safe", "severity": 1, "explanation": "clean"}'
        with patch.object(mod, "chat", return_value=llm_resp):
            resp = self.client.post("/moderate", json={"text": "hello"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["text"] == "hello"
            assert data["result"]["category"] == "safe"

    def test_batch_moderate_endpoint(self, mod):
        llm_resp = '{"category": "safe", "severity": 1, "explanation": "ok"}'
        with patch.object(mod, "chat", return_value=llm_resp):
            resp = self.client.post("/moderate/batch", json={"texts": ["a", "b"]})
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 2
            assert data[0]["text"] == "a"
            assert data[1]["text"] == "b"
