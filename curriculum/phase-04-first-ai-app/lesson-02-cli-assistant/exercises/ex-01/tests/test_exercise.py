"""Tests for Exercise 1 — CLI Assistant Utilities."""

import importlib.util
import json
import os
import tempfile
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


@pytest.fixture
def sample_messages():
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm doing well, thanks!"},
    ]


# ---------------------------------------------------------------------------
# Tests — create_system_prompt
# ---------------------------------------------------------------------------

def test_create_system_prompt_basic(mod):
    """Should format the system prompt correctly."""
    result = mod.create_system_prompt("Aria", "You are friendly.")
    assert result == "You are Aria, an AI assistant. You are friendly. Keep responses concise and helpful."


def test_create_system_prompt_different_name(mod):
    """Should include the given name."""
    result = mod.create_system_prompt("CodeBot", "You help with Python.")
    assert "CodeBot" in result


def test_create_system_prompt_includes_personality(mod):
    """Should include the personality description."""
    result = mod.create_system_prompt("AI", "Be creative and fun.")
    assert "Be creative and fun." in result


def test_create_system_prompt_includes_concise(mod):
    """Should include the 'concise and helpful' instruction."""
    result = mod.create_system_prompt("AI", "Be nice.")
    assert "Keep responses concise and helpful." in result


# ---------------------------------------------------------------------------
# Tests — format_history
# ---------------------------------------------------------------------------

def test_format_history_basic(mod, sample_messages):
    """Should format user and assistant messages correctly."""
    result = mod.format_history(sample_messages)
    assert "You: Hello!" in result
    assert "AI: Hi there!" in result


def test_format_history_skips_system(mod, sample_messages):
    """Should not include system messages."""
    result = mod.format_history(sample_messages)
    assert "system" not in result.lower() or "You are" not in result


def test_format_history_preserves_order(mod, sample_messages):
    """Messages should appear in order."""
    result = mod.format_history(sample_messages)
    lines = result.split("\n")
    assert lines[0] == "You: Hello!"
    assert lines[1] == "AI: Hi there!"
    assert lines[2] == "You: How are you?"
    assert lines[3] == "AI: I'm doing well, thanks!"


def test_format_history_empty(mod):
    """Empty messages should return empty string."""
    result = mod.format_history([])
    assert result == ""


def test_format_history_system_only(mod):
    """Only system messages should return empty string."""
    result = mod.format_history([{"role": "system", "content": "test"}])
    assert result == ""


# ---------------------------------------------------------------------------
# Tests — save_conversation
# ---------------------------------------------------------------------------

def test_save_conversation_writes_json(mod, sample_messages):
    """Should write valid JSON to file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        filepath = tmp.name

    try:
        mod.save_conversation(sample_messages, filepath)
        with open(filepath, "r") as f:
            loaded = json.load(f)
        assert loaded == sample_messages
    finally:
        os.unlink(filepath)


def test_save_conversation_formatted(mod, sample_messages):
    """Should write indented JSON."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        filepath = tmp.name

    try:
        mod.save_conversation(sample_messages, filepath)
        with open(filepath, "r") as f:
            content = f.read()
        # Indented JSON will have newlines
        assert "\n" in content
    finally:
        os.unlink(filepath)


# ---------------------------------------------------------------------------
# Tests — load_conversation
# ---------------------------------------------------------------------------

def test_load_conversation_reads_json(mod, sample_messages):
    """Should load messages from a JSON file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        json.dump(sample_messages, tmp)
        filepath = tmp.name

    try:
        result = mod.load_conversation(filepath)
        assert result == sample_messages
    finally:
        os.unlink(filepath)


def test_load_conversation_file_not_found(mod):
    """Should return empty list if file doesn't exist."""
    result = mod.load_conversation("/nonexistent/path/chat.json")
    assert result == []


def test_load_conversation_returns_list(mod, sample_messages):
    """Should return a list."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        json.dump(sample_messages, tmp)
        filepath = tmp.name

    try:
        result = mod.load_conversation(filepath)
        assert isinstance(result, list)
    finally:
        os.unlink(filepath)
