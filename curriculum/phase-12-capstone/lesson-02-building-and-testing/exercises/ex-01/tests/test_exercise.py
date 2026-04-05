"""Tests for Exercise 1 — AI Testing Utilities."""

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
# Tests — mock_llm
# ---------------------------------------------------------------------------

def test_mock_llm_returns_responses(mod):
    """mock_llm should return responses in order."""
    fake = mod.mock_llm(["first", "second", "third"])
    assert fake("any prompt") == "first"
    assert fake("any prompt") == "second"
    assert fake("any prompt") == "third"


def test_mock_llm_cycles(mod):
    """mock_llm should cycle back to the start."""
    fake = mod.mock_llm(["a", "b"])
    fake("x")  # a
    fake("x")  # b
    assert fake("x") == "a"  # cycles back


# ---------------------------------------------------------------------------
# Tests — LLMTestHarness.test_prompt
# ---------------------------------------------------------------------------

def test_prompt_expected_keywords_pass(mod):
    """test_prompt should pass when expected keywords are found."""
    fake = mod.mock_llm(["The capital of France is Paris."])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_prompt("test", expected_keywords=["Paris", "France"])
    assert result["passed"] is True


def test_prompt_expected_keywords_fail(mod):
    """test_prompt should fail when expected keywords are missing."""
    fake = mod.mock_llm(["Hello world"])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_prompt("test", expected_keywords=["Paris"])
    assert result["passed"] is False


def test_prompt_unexpected_keywords(mod):
    """test_prompt should fail when unexpected keywords are found."""
    fake = mod.mock_llm(["This contains bad content"])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_prompt("test", unexpected_keywords=["bad"])
    assert result["passed"] is False


def test_prompt_max_length(mod):
    """test_prompt should fail when response exceeds max_length."""
    fake = mod.mock_llm(["A very long response " * 50])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_prompt("test", max_length=10)
    assert result["passed"] is False


def test_prompt_returns_response(mod):
    """test_prompt should include the actual response."""
    fake = mod.mock_llm(["Hello!"])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_prompt("test")
    assert result["response"] == "Hello!"


# ---------------------------------------------------------------------------
# Tests — LLMTestHarness.test_consistency
# ---------------------------------------------------------------------------

def test_consistency_identical(mod):
    """Identical responses should be consistent."""
    fake = mod.mock_llm(["same answer"])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_consistency("test", runs=3)
    assert result["consistent"] is True
    assert result["similarity_ratio"] == 1.0


def test_consistency_different(mod):
    """Different responses should not be consistent."""
    fake = mod.mock_llm(["answer 1", "answer 2", "answer 3"])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_consistency("test", runs=3)
    assert result["consistent"] is False


# ---------------------------------------------------------------------------
# Tests — LLMTestHarness.test_format
# ---------------------------------------------------------------------------

def test_format_valid_json(mod):
    """Valid JSON response should pass JSON format check."""
    fake = mod.mock_llm(['{"key": "value"}'])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_format("test", "json")
    assert result["passed"] is True


def test_format_invalid_json(mod):
    """Invalid JSON response should fail JSON format check."""
    fake = mod.mock_llm(["not json at all"])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_format("test", "json")
    assert result["passed"] is False


def test_format_markdown(mod):
    """Response with header should pass markdown check."""
    fake = mod.mock_llm(["# Title\n\nSome content"])
    harness = mod.LLMTestHarness(fake)
    result = harness.test_format("test", "markdown")
    assert result["passed"] is True


# ---------------------------------------------------------------------------
# Tests — run_test_suite
# ---------------------------------------------------------------------------

def test_suite_counts(mod):
    """Test suite should count passed and failed correctly."""
    fake = mod.mock_llm(["Paris is great"])
    harness = mod.LLMTestHarness(fake)
    results = harness.run_test_suite([
        {"name": "pass_test", "prompt": "test", "checks": {"expected_keywords": ["Paris"]}},
        {"name": "fail_test", "prompt": "test", "checks": {"expected_keywords": ["London"]}},
    ])
    assert results["total"] == 2
    assert results["passed"] == 1
    assert results["failed"] == 1


# ---------------------------------------------------------------------------
# Tests — evaluate_quality
# ---------------------------------------------------------------------------

def test_evaluate_exact_match_true(mod):
    """Identical strings should have exact_match True."""
    result = mod.evaluate_quality("hello", "hello")
    assert result["exact_match"] is True


def test_evaluate_exact_match_false(mod):
    """Different strings should have exact_match False."""
    result = mod.evaluate_quality("hello", "world")
    assert result["exact_match"] is False


def test_evaluate_keyword_overlap(mod):
    """Keyword overlap should be between 0 and 1."""
    result = mod.evaluate_quality(
        "Paris is the capital of France",
        "The capital of France is Paris",
    )
    assert 0 <= result["keyword_overlap"] <= 1
    assert result["keyword_overlap"] > 0.5  # Most words overlap


def test_evaluate_length_ratio(mod):
    """Length ratio should reflect relative lengths."""
    result = mod.evaluate_quality("short", "a much longer reference string")
    assert result["length_ratio"] < 1.0


def test_evaluate_length_ratio_capped(mod):
    """Length ratio should be capped at 2.0."""
    result = mod.evaluate_quality("a" * 1000, "short")
    assert result["length_ratio"] == 2.0
