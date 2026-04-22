"""Tests for Project 07: AI-Powered API."""

import importlib.util
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
    with patch("httpx.post") as mock_post:
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


class TestChat:
    """Tests for chat() helper."""

    def test_chat_returns_string(self, mod):
        with patch("httpx.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "hello"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.chat("system", "user msg")
            assert result == "hello"

    def test_chat_raises_http_exception_on_failure(self, mod):
        """chat() should raise HTTPException when Ollama is unavailable."""
        from fastapi import HTTPException

        with patch("httpx.post") as mock_post:
            mock_post.side_effect = Exception("connection refused")

            with pytest.raises(HTTPException) as exc_info:
                mod.chat("sys", "usr")
            assert exc_info.value.status_code == 503


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "model" in data


class TestSummarizeEndpoint:
    """Tests for POST /summarize."""

    def test_summarize_success(self, mod, client):
        with patch("httpx.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "message": {"content": "A brief summary."}
            }
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            resp = client.post("/summarize", json={"text": "Long text here..."})
            assert resp.status_code == 200
            assert resp.json()["result"] == "A brief summary."

    def test_summarize_missing_text(self, client):
        """POST /summarize without text should return 422."""
        resp = client.post("/summarize", json={})
        assert resp.status_code == 422


class TestClassifyEndpoint:
    """Tests for POST /classify."""

    def test_classify_success(self, mod, client):
        with patch("httpx.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "message": {"content": "Technology"}
            }
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            resp = client.post(
                "/classify",
                json={
                    "text": "Python is great for AI",
                    "categories": ["Technology", "Sports", "Food"],
                },
            )
            assert resp.status_code == 200
            assert resp.json()["result"] == "Technology"

    def test_classify_includes_categories_in_prompt(self, mod, client):
        """The classify prompt should include the provided categories."""
        with patch("httpx.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "A"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            client.post(
                "/classify",
                json={"text": "test", "categories": ["A", "B", "C"]},
            )
            payload = mock_post.call_args[1]["json"]
            system_prompt = payload["messages"][0]["content"]
            assert "A" in system_prompt and "B" in system_prompt and "C" in system_prompt

    def test_classify_missing_fields(self, client):
        """POST /classify without categories should return 422."""
        resp = client.post("/classify", json={"text": "hello"})
        assert resp.status_code == 422


class TestGenerateEndpoint:
    """Tests for POST /generate."""

    def test_generate_success(self, mod, client):
        with patch("httpx.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "message": {"content": "Generated text here."}
            }
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            resp = client.post("/generate", json={"prompt": "Write a poem"})
            assert resp.status_code == 200
            assert resp.json()["result"] == "Generated text here."

    def test_generate_missing_prompt(self, client):
        """POST /generate without prompt should return 422."""
        resp = client.post("/generate", json={})
        assert resp.status_code == 422


class TestPydanticModels:
    """Tests for request/response Pydantic models."""

    def test_summarize_request_model(self, mod):
        req = mod.SummarizeRequest(text="hello")
        assert req.text == "hello"

    def test_classify_request_model(self, mod):
        req = mod.ClassifyRequest(text="hi", categories=["A", "B"])
        assert req.categories == ["A", "B"]

    def test_generate_request_defaults(self, mod):
        req = mod.GenerateRequest(prompt="test")
        assert req.max_tokens == 200

    def test_ai_response_model(self, mod):
        resp = mod.AIResponse(result="output")
        assert resp.result == "output"
