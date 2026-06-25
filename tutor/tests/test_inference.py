"""Tests for the inference backend abstraction (Ollama vs OpenAI-compatible)."""

import json

import httpx
import pytest

from tutor.config import settings
from tutor.engine.inference import (
    OpenAICompatBackend,
    get_inference_backend,
)
from tutor.engine.ollama_client import ollama_client


def test_factory_defaults_to_ollama(monkeypatch):
    """With the default backend, the factory returns the shared Ollama client."""
    monkeypatch.setattr(settings, "inference_backend", "ollama")
    assert get_inference_backend() is ollama_client


def test_factory_selects_openai_compat(monkeypatch):
    """Setting the backend to openai_compat yields an OpenAICompatBackend."""
    monkeypatch.setattr(settings, "inference_backend", "openai_compat")
    assert isinstance(get_inference_backend(), OpenAICompatBackend)


@pytest.mark.asyncio
async def test_openai_compat_non_stream(monkeypatch):
    """Non-streaming chat extracts choices[0].message.content and posts the
    request to /chat/completions with the configured model."""
    monkeypatch.setattr(settings, "inference_base_url", "http://test/v1")
    monkeypatch.setattr(settings, "inference_model", "llama3.2:3b")
    monkeypatch.setattr(settings, "inference_max_tokens", 256)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")
        body = json.loads(request.content)
        assert body["model"] == "llama3.2:3b"
        assert body["stream"] is False
        assert body["max_tokens"] == 256
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "hello world"}}]}
        )

    backend = OpenAICompatBackend()
    backend._client = httpx.AsyncClient(
        base_url="http://test/v1", transport=httpx.MockTransport(handler)
    )
    out = await backend.chat([{"role": "user", "content": "hi"}], stream=False)
    assert out == "hello world"
    await backend.close()


@pytest.mark.asyncio
async def test_openai_compat_stream(monkeypatch):
    """Streaming chat parses SSE delta chunks and stops at [DONE]."""
    monkeypatch.setattr(settings, "inference_base_url", "http://test/v1")
    sse = (
        'data: {"choices":[{"delta":{"content":"Hel"}}]}\n\n'
        'data: {"choices":[{"delta":{"content":"lo"}}]}\n\n'
        "data: [DONE]\n\n"
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=sse.encode())

    backend = OpenAICompatBackend()
    backend._client = httpx.AsyncClient(
        base_url="http://test/v1", transport=httpx.MockTransport(handler)
    )
    stream = await backend.chat([{"role": "user", "content": "hi"}], stream=True)
    chunks = [chunk async for chunk in stream]
    assert "".join(chunks) == "Hello"
    await backend.close()


@pytest.mark.asyncio
async def test_openai_compat_health_no_base_url(monkeypatch):
    """An unconfigured base URL reports unhealthy rather than raising."""
    monkeypatch.setattr(settings, "inference_base_url", "")
    backend = OpenAICompatBackend()
    assert await backend.check_health() is False
