"""Tests for Exercise 1 — Structured Output Parsers."""

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
# Tests — extract_json
# ---------------------------------------------------------------------------

def test_extract_json_clean(mod):
    """Should parse a clean JSON string."""
    result = mod.extract_json('{"name": "Widget", "price": 9.99}')
    assert result == {"name": "Widget", "price": 9.99}


def test_extract_json_with_surrounding_text(mod):
    """Should extract JSON from text with surrounding content."""
    text = "Here's the data:\n{\"key\": \"value\"}\nHope that helps!"
    result = mod.extract_json(text)
    assert result == {"key": "value"}


def test_extract_json_no_json(mod):
    """Should return None when no JSON is present."""
    result = mod.extract_json("This is just plain text with no JSON.")
    assert result is None


def test_extract_json_invalid_json(mod):
    """Should return None for malformed JSON."""
    result = mod.extract_json("{invalid json content}")
    assert result is None


def test_extract_json_multiline(mod):
    """Should handle multiline JSON."""
    text = 'Result:\n{\n  "a": 1,\n  "b": 2\n}\nDone.'
    result = mod.extract_json(text)
    assert result == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# Tests — extract_markdown_sections
# ---------------------------------------------------------------------------

def test_markdown_single_section(mod):
    """Should parse a single section."""
    text = "# Title\nSome content here."
    result = mod.extract_markdown_sections(text)
    assert "Title" in result
    assert result["Title"] == "Some content here."


def test_markdown_multiple_sections(mod):
    """Should parse multiple sections."""
    text = "# Summary\nLooks good.\n\n# Issues\n- Bug found.\n\n# Fix\nApply patch."
    result = mod.extract_markdown_sections(text)
    assert len(result) == 3
    assert "Summary" in result
    assert "Issues" in result
    assert "Fix" in result


def test_markdown_different_levels(mod):
    """Should handle ## and ### headings."""
    text = "## Overview\nContent A.\n### Details\nContent B."
    result = mod.extract_markdown_sections(text)
    assert "Overview" in result
    assert "Details" in result


def test_markdown_empty_text(mod):
    """Should return empty dict for text without headings."""
    result = mod.extract_markdown_sections("No headings here.")
    assert result == {}


def test_markdown_strips_content(mod):
    """Content should be stripped of leading/trailing whitespace."""
    text = "# Section\n\n  Some content  \n\n"
    result = mod.extract_markdown_sections(text)
    assert result["Section"] == "Some content"


# ---------------------------------------------------------------------------
# Tests — create_json_prompt
# ---------------------------------------------------------------------------

def test_json_prompt_contains_task(mod):
    """Prompt should contain the task description."""
    result = mod.create_json_prompt("Extract info", "name (string)", '{"name": "X"}')
    assert "Extract info" in result


def test_json_prompt_contains_schema(mod):
    """Prompt should contain the schema description."""
    result = mod.create_json_prompt("Task", "name (string), price (number)", '{}')
    assert "name (string), price (number)" in result


def test_json_prompt_contains_example(mod):
    """Prompt should contain the example output."""
    result = mod.create_json_prompt("Task", "fields", '{"name": "Example"}')
    assert '{"name": "Example"}' in result


def test_json_prompt_contains_json_instruction(mod):
    """Prompt should instruct to return only JSON."""
    result = mod.create_json_prompt("Task", "fields", "{}")
    assert "ONLY" in result
    assert "JSON" in result


# ---------------------------------------------------------------------------
# Tests — validate_llm_json
# ---------------------------------------------------------------------------

def test_validate_valid_json_all_fields(mod):
    """Should validate when JSON has all required fields."""
    text = '{"name": "Widget", "price": 9.99}'
    result = mod.validate_llm_json(text, ["name", "price"])
    assert result["valid"] is True
    assert result["data"] == {"name": "Widget", "price": 9.99}
    assert result["missing_fields"] == []


def test_validate_missing_fields(mod):
    """Should detect missing required fields."""
    text = '{"name": "Widget"}'
    result = mod.validate_llm_json(text, ["name", "price", "rating"])
    assert result["valid"] is False
    assert "price" in result["missing_fields"]
    assert "rating" in result["missing_fields"]


def test_validate_no_json(mod):
    """Should handle text with no JSON."""
    result = mod.validate_llm_json("No JSON here", ["name"])
    assert result["valid"] is False
    assert result["data"] is None
    assert "name" in result["missing_fields"]


def test_validate_json_in_surrounding_text(mod):
    """Should extract and validate JSON from surrounding text."""
    text = "Here you go:\n{\"x\": 1, \"y\": 2}\nAll done."
    result = mod.validate_llm_json(text, ["x", "y"])
    assert result["valid"] is True
    assert result["data"]["x"] == 1
