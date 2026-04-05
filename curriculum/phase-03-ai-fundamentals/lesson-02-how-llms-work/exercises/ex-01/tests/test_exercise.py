"""Tests for Exercise 1 — Simple Tokenizer."""

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
# Tests — simple_tokenize
# ---------------------------------------------------------------------------

def test_tokenize_simple_sentence(mod):
    """Should split words and punctuation."""
    result = mod.simple_tokenize("Hello, world!")
    assert result == ["Hello", ",", "world", "!"]


def test_tokenize_no_punctuation(mod):
    """Should handle text without punctuation."""
    result = mod.simple_tokenize("hello world")
    assert result == ["hello", "world"]


def test_tokenize_multiple_punctuation(mod):
    """Should handle multiple punctuation marks."""
    result = mod.simple_tokenize("Wait... really?!")
    assert "Wait" in result
    assert result.count(".") == 3


def test_tokenize_empty_string(mod):
    """Empty string should return empty list."""
    result = mod.simple_tokenize("")
    assert result == []


def test_tokenize_returns_list(mod):
    """Should return a list."""
    result = mod.simple_tokenize("test")
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Tests — count_tokens
# ---------------------------------------------------------------------------

def test_count_tokens_simple(mod):
    """Should count tokens correctly."""
    result = mod.count_tokens("Hello, world!")
    assert result == 4  # Hello, comma, world, !


def test_count_tokens_empty(mod):
    """Empty string should have 0 tokens."""
    assert mod.count_tokens("") == 0


def test_count_tokens_returns_int(mod):
    """Should return an integer."""
    result = mod.count_tokens("test")
    assert isinstance(result, int)


# ---------------------------------------------------------------------------
# Tests — estimate_cost
# ---------------------------------------------------------------------------

def test_estimate_cost_basic(mod):
    """Should calculate cost correctly."""
    # 4 tokens at $0.002 per 1K = 4/1000 * 0.002 = 0.000008
    result = mod.estimate_cost("Hello, world!", 0.002)
    assert result == 0.000008


def test_estimate_cost_zero_tokens(mod):
    """Empty text should cost nothing."""
    result = mod.estimate_cost("", 0.002)
    assert result == 0.0


def test_estimate_cost_different_price(mod):
    """Should work with different price points."""
    # 4 tokens at $0.01 per 1K = 4/1000 * 0.01 = 0.00004
    result = mod.estimate_cost("Hello, world!", 0.01)
    assert result == 0.00004


def test_estimate_cost_returns_float(mod):
    """Should return a float."""
    result = mod.estimate_cost("test", 0.002)
    assert isinstance(result, float)
