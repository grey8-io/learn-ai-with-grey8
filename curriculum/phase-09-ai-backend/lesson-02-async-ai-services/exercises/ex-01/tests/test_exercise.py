"""Tests for Exercise 1 — Async AI Service Utilities."""

import asyncio
import importlib.util
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "solution", "main.py"
)


def _load_module(path: str):
    """Import main.py as a module from the given path."""
    spec = importlib.util.spec_from_file_location("student_main", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    return _load_module(SOLUTION_PATH)


# ---------------------------------------------------------------------------
# Tests — AsyncLLMClient init
# ---------------------------------------------------------------------------

def test_client_stores_base_url(mod):
    """Client should store base_url with trailing slash stripped."""
    client = mod.AsyncLLMClient("http://localhost:11434/", timeout=10.0)
    assert client.base_url == "http://localhost:11434"
    assert client.timeout == 10.0


def test_client_default_timeout(mod):
    """Client should default to 30.0 second timeout."""
    client = mod.AsyncLLMClient("http://localhost:11434")
    assert client.timeout == 30.0


# ---------------------------------------------------------------------------
# Tests — generate
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_generate_calls_api(mod):
    """generate() should POST to /api/generate and return response text."""
    client = mod.AsyncLLMClient("http://localhost:11434")

    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Hello from LLM"}

    mock_async_client = AsyncMock()
    mock_async_client.post.return_value = mock_response
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_async_client):
        result = await client.generate("test prompt", model="llama3")

    assert result == "Hello from LLM"
    mock_async_client.post.assert_called_once()


# ---------------------------------------------------------------------------
# Tests — batch_generate
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_batch_generate_returns_all_results(mod):
    """batch_generate() should return results for all prompts."""
    client = mod.AsyncLLMClient("http://localhost:11434")

    call_count = 0

    async def mock_generate(prompt, model="default"):
        nonlocal call_count
        call_count += 1
        return f"response_{call_count}"

    client.generate = mock_generate
    results = await client.batch_generate(["a", "b", "c"], max_concurrent=2)

    assert len(results) == 3
    assert all(r.startswith("response_") for r in results)


# ---------------------------------------------------------------------------
# Tests — retry_with_backoff
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_succeeds_on_first_try(mod):
    """retry_with_backoff should return immediately on success."""
    call_count = 0

    async def succeed():
        nonlocal call_count
        call_count += 1
        return "ok"

    result = await mod.retry_with_backoff(succeed, max_retries=3, base_delay=0.01)
    assert result == "ok"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_retries_on_failure(mod):
    """retry_with_backoff should retry and eventually succeed."""
    call_count = 0

    async def fail_then_succeed():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("temporary failure")
        return "recovered"

    result = await mod.retry_with_backoff(
        fail_then_succeed, max_retries=3, base_delay=0.01
    )
    assert result == "recovered"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_raises_after_max_retries(mod):
    """retry_with_backoff should raise after all retries are exhausted."""
    async def always_fail():
        raise ValueError("permanent failure")

    with pytest.raises(ValueError, match="permanent failure"):
        await mod.retry_with_backoff(always_fail, max_retries=2, base_delay=0.01)


# ---------------------------------------------------------------------------
# Tests — create_sse_response
# ---------------------------------------------------------------------------

def test_sse_format(mod):
    """create_sse_response should format chunks as SSE data lines."""
    result = mod.create_sse_response(["Hello", " world"])
    assert result == ["data: Hello\n\n", "data:  world\n\n"]


def test_sse_empty_list(mod):
    """create_sse_response should handle empty input."""
    result = mod.create_sse_response([])
    assert result == []
