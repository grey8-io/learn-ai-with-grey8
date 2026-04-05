"""Tests for Exercise 1 — OllamaChat Client."""

import importlib.util
import json
import os
from unittest.mock import MagicMock, patch, call
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


def _make_mock_response(content: str) -> MagicMock:
    """Create a mock httpx response."""
    mock = MagicMock()
    mock.json.return_value = {
        "model": "tinyllama",
        "message": {"role": "assistant", "content": content},
        "done": True,
    }
    mock.raise_for_status = MagicMock()
    return mock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    return _load_module(SOLUTION_PATH)


# ---------------------------------------------------------------------------
# Tests — __init__
# ---------------------------------------------------------------------------

def test_default_model(mod):
    """Default model should be tinyllama."""
    chat = mod.OllamaChat()
    assert chat.model == "tinyllama"


def test_default_host(mod):
    """Default host should be localhost:11434."""
    chat = mod.OllamaChat()
    assert chat.host == "http://localhost:11434"


def test_custom_model(mod):
    """Should accept a custom model name."""
    chat = mod.OllamaChat(model="llama2")
    assert chat.model == "llama2"


def test_custom_host(mod):
    """Should accept a custom host."""
    chat = mod.OllamaChat(host="http://myserver:11434")
    assert chat.host == "http://myserver:11434"


# ---------------------------------------------------------------------------
# Tests — send
# ---------------------------------------------------------------------------

def test_send_returns_content(mod):
    """send() should return the assistant's message content."""
    chat = mod.OllamaChat()
    mock_resp = _make_mock_response("Hello there!")

    with patch("httpx.post", return_value=mock_resp):
        result = chat.send("Hi")

    assert result == "Hello there!"


def test_send_posts_correct_url(mod):
    """send() should POST to the correct URL."""
    chat = mod.OllamaChat()
    mock_resp = _make_mock_response("response")

    with patch("httpx.post", return_value=mock_resp) as mock_post:
        chat.send("Hi")

    args, kwargs = mock_post.call_args
    assert args[0] == "http://localhost:11434/api/chat"


def test_send_includes_model(mod):
    """send() should include the model in the request."""
    chat = mod.OllamaChat(model="llama2")
    mock_resp = _make_mock_response("response")

    with patch("httpx.post", return_value=mock_resp) as mock_post:
        chat.send("Hi")

    _, kwargs = mock_post.call_args
    assert kwargs["json"]["model"] == "llama2"


def test_send_without_system_prompt(mod):
    """send() without system_prompt should only include user message."""
    chat = mod.OllamaChat()
    mock_resp = _make_mock_response("response")

    with patch("httpx.post", return_value=mock_resp) as mock_post:
        chat.send("Hello")

    _, kwargs = mock_post.call_args
    messages = kwargs["json"]["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"


def test_send_with_system_prompt(mod):
    """send() with system_prompt should include system and user messages."""
    chat = mod.OllamaChat()
    mock_resp = _make_mock_response("response")

    with patch("httpx.post", return_value=mock_resp) as mock_post:
        chat.send("Hello", system_prompt="Be brief.")

    _, kwargs = mock_post.call_args
    messages = kwargs["json"]["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "Be brief."
    assert messages[1]["role"] == "user"


def test_send_sets_stream_false(mod):
    """send() should set stream to False."""
    chat = mod.OllamaChat()
    mock_resp = _make_mock_response("response")

    with patch("httpx.post", return_value=mock_resp) as mock_post:
        chat.send("Hi")

    _, kwargs = mock_post.call_args
    assert kwargs["json"]["stream"] is False


# ---------------------------------------------------------------------------
# Tests — send_with_history
# ---------------------------------------------------------------------------

def test_send_with_history_returns_content(mod):
    """send_with_history() should return the assistant's message content."""
    chat = mod.OllamaChat()
    mock_resp = _make_mock_response("Ahoy!")

    messages = [
        {"role": "system", "content": "You are a pirate."},
        {"role": "user", "content": "Hello"},
    ]

    with patch("httpx.post", return_value=mock_resp):
        result = chat.send_with_history(messages)

    assert result == "Ahoy!"


def test_send_with_history_passes_messages(mod):
    """send_with_history() should pass the full message list."""
    chat = mod.OllamaChat()
    mock_resp = _make_mock_response("response")

    messages = [
        {"role": "user", "content": "First question"},
        {"role": "assistant", "content": "First answer"},
        {"role": "user", "content": "Follow-up"},
    ]

    with patch("httpx.post", return_value=mock_resp) as mock_post:
        chat.send_with_history(messages)

    _, kwargs = mock_post.call_args
    assert kwargs["json"]["messages"] == messages


def test_send_with_history_calls_raise_for_status(mod):
    """send_with_history() should call raise_for_status."""
    chat = mod.OllamaChat()
    mock_resp = _make_mock_response("response")

    with patch("httpx.post", return_value=mock_resp):
        chat.send_with_history([{"role": "user", "content": "Hi"}])

    mock_resp.raise_for_status.assert_called_once()
