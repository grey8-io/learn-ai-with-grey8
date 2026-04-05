"""Tests for Exercise 1 — Prompt Engineering Utilities."""

import importlib.util
import os
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
# Tests — create_system_prompt
# ---------------------------------------------------------------------------

def test_system_prompt_contains_role(mod):
    """System prompt should contain the role."""
    result = mod.create_system_prompt("Python tutor", "beginner Python", "friendly", "be brief")
    assert "Python tutor" in result


def test_system_prompt_contains_all_components(mod):
    """System prompt should contain all four components."""
    result = mod.create_system_prompt("code reviewer", "clean code", "direct", "under 200 words")
    assert "code reviewer" in result
    assert "clean code" in result
    assert "direct" in result
    assert "under 200 words" in result


def test_system_prompt_format(mod):
    """System prompt should follow the expected multi-line format."""
    result = mod.create_system_prompt("translator", "languages", "formal", "be accurate")
    lines = result.strip().split("\n")
    assert len(lines) == 4
    assert lines[0].startswith("You are a")
    assert "specialize" in lines[1].lower()
    assert "tone" in lines[2].lower()
    assert "constraint" in lines[3].lower()


# ---------------------------------------------------------------------------
# Tests — create_few_shot_prompt
# ---------------------------------------------------------------------------

def test_few_shot_contains_task(mod):
    """Few-shot prompt should start with the task description."""
    result = mod.create_few_shot_prompt("Classify sentiment", [], "hello")
    assert result.startswith("Task: Classify sentiment")


def test_few_shot_contains_examples(mod):
    """Few-shot prompt should contain all examples."""
    examples = [
        {"input": "I love it", "output": "POSITIVE"},
        {"input": "I hate it", "output": "NEGATIVE"},
    ]
    result = mod.create_few_shot_prompt("Classify", examples, "test")
    assert "Input: I love it" in result
    assert "Output: POSITIVE" in result
    assert "Input: I hate it" in result
    assert "Output: NEGATIVE" in result


def test_few_shot_contains_query(mod):
    """Few-shot prompt should end with the query."""
    result = mod.create_few_shot_prompt("Classify", [], "It works fine.")
    assert "Input: It works fine." in result
    assert result.rstrip().endswith("Output:")


def test_few_shot_has_perform_section(mod):
    """Few-shot prompt should include 'Now perform the task' section."""
    result = mod.create_few_shot_prompt("Translate", [], "hello")
    assert "Now perform the task:" in result


# ---------------------------------------------------------------------------
# Tests — validate_prompt
# ---------------------------------------------------------------------------

def test_validate_valid_prompt(mod):
    """A normal prompt should be valid."""
    result = mod.validate_prompt("Tell me about Python.")
    assert result["valid"] is True
    assert result["issues"] == []
    assert result["estimated_tokens"] == len("Tell me about Python.") // 4


def test_validate_empty_prompt(mod):
    """An empty prompt should be invalid."""
    result = mod.validate_prompt("")
    assert result["valid"] is False
    assert any("empty" in issue.lower() for issue in result["issues"])


def test_validate_whitespace_prompt(mod):
    """A whitespace-only prompt should be invalid."""
    result = mod.validate_prompt("   \n\t  ")
    assert result["valid"] is False
    assert any("empty" in issue.lower() for issue in result["issues"])


def test_validate_exceeds_token_limit(mod):
    """A long prompt should exceed the token limit."""
    long_prompt = "word " * 1000  # ~5000 chars = ~1250 tokens
    result = mod.validate_prompt(long_prompt, max_tokens=100)
    assert result["valid"] is False
    assert any("token limit" in issue.lower() for issue in result["issues"])


def test_validate_token_estimation(mod):
    """Token estimation should be chars // 4."""
    prompt = "a" * 100  # exactly 100 chars = 25 tokens
    result = mod.validate_prompt(prompt)
    assert result["estimated_tokens"] == 25
