"""Tests for Exercise 1 — Talk to a Local AI.

These tests mock the Ollama API so you can run them without Ollama running.
"""

import importlib.util
import json
import os
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "solution", "main.py"
)


def _load_module(path: str):
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


class FakeResponse:
    """Minimal stand-in for an httpx.Response."""

    def __init__(self, payload: dict):
        self._payload = payload
        self.status_code = 200

    def json(self):
        return self._payload


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_ask_ollama_exists(mod):
    """A callable function named ask_ollama should exist."""
    assert hasattr(mod, "ask_ollama"), "Function 'ask_ollama' is not defined"
    assert callable(mod.ask_ollama), "'ask_ollama' should be a callable function"


def test_ask_ollama_calls_api_correctly(mod, monkeypatch):
    """ask_ollama should POST to the correct URL with the right JSON body."""
    captured = {}

    def fake_post(url, *, json=None, timeout=None, **kwargs):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse({"response": "Python is great."})

    monkeypatch.setattr(mod.httpx, "post", fake_post)

    result = mod.ask_ollama("What is Python?")

    assert captured["url"] == "http://localhost:11434/api/generate"
    assert captured["json"]["model"] == "tinyllama"
    assert captured["json"]["prompt"] == "What is Python?"
    assert captured["json"]["stream"] is False
    assert result == "Python is great."


def test_ask_ollama_custom_model(mod, monkeypatch):
    """ask_ollama should accept a custom model name."""
    captured = {}

    def fake_post(url, *, json=None, timeout=None, **kwargs):
        captured["json"] = json
        return FakeResponse({"response": "Sure thing."})

    monkeypatch.setattr(mod.httpx, "post", fake_post)

    mod.ask_ollama("Hello", model="llama3.2:1b")
    assert captured["json"]["model"] == "llama3.2:1b"


def test_ask_ollama_returns_string(mod, monkeypatch):
    """ask_ollama should return a string."""

    def fake_post(url, *, json=None, timeout=None, **kwargs):
        return FakeResponse({"response": "42"})

    monkeypatch.setattr(mod.httpx, "post", fake_post)

    result = mod.ask_ollama("What is the meaning of life?")
    assert isinstance(result, str)


def test_ask_ollama_sets_timeout(mod, monkeypatch):
    """ask_ollama should set a reasonable timeout (>= 10 seconds)."""
    captured = {}

    def fake_post(url, *, json=None, timeout=None, **kwargs):
        captured["timeout"] = timeout
        return FakeResponse({"response": "ok"})

    monkeypatch.setattr(mod.httpx, "post", fake_post)

    mod.ask_ollama("test")
    assert captured["timeout"] is not None, "A timeout should be set"
    assert captured["timeout"] >= 10, "Timeout should be at least 10 seconds"
