"""Tests for Exercise 1 — Token & Cost Management."""

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
# Tests — estimate_tokens
# ---------------------------------------------------------------------------

def test_estimate_tokens_basic(mod):
    """estimate_tokens should return len(text) // 4."""
    assert mod.estimate_tokens("Hello World!") == 3  # 12 chars // 4
    assert mod.estimate_tokens("") == 0
    assert mod.estimate_tokens("a" * 100) == 25


# ---------------------------------------------------------------------------
# Tests — CostTracker
# ---------------------------------------------------------------------------

def test_cost_tracker_single_record(mod):
    """Tracking one call should produce correct cost."""
    tracker = mod.CostTracker(price_per_1k_input=0.01, price_per_1k_output=0.03)
    # "Hello" = 1 token input, "World!" = 1 token output
    tracker.track("abcd" * 10, "abcd" * 5, "test-model")  # 10 input, 5 output tokens
    cost = tracker.get_total_cost()
    expected = (10 / 1000 * 0.01) + (5 / 1000 * 0.03)
    assert cost == pytest.approx(expected)


def test_cost_tracker_usage_report(mod):
    """get_usage_report should aggregate all records."""
    tracker = mod.CostTracker(price_per_1k_input=0.01, price_per_1k_output=0.03)
    tracker.track("a" * 40, "b" * 80)  # 10 input, 20 output
    tracker.track("c" * 40, "d" * 80)  # 10 input, 20 output
    report = tracker.get_usage_report()
    assert report["total_requests"] == 2
    assert report["total_input_tokens"] == 20
    assert report["total_output_tokens"] == 40
    assert report["avg_cost_per_request"] == pytest.approx(report["total_cost"] / 2)


def test_cost_tracker_empty_report(mod):
    """Empty tracker should return zeroed report."""
    tracker = mod.CostTracker(price_per_1k_input=0.01, price_per_1k_output=0.03)
    report = tracker.get_usage_report()
    assert report["total_requests"] == 0
    assert report["total_cost"] == 0.0
    assert report["avg_cost_per_request"] == 0.0


def test_cost_tracker_model_breakdown(mod):
    """get_model_breakdown should group by model."""
    tracker = mod.CostTracker(price_per_1k_input=0.01, price_per_1k_output=0.03)
    tracker.track("a" * 40, "b" * 40, "gpt-4")
    tracker.track("c" * 40, "d" * 40, "gpt-4")
    tracker.track("e" * 40, "f" * 40, "gpt-3.5")
    breakdown = tracker.get_model_breakdown()
    assert "gpt-4" in breakdown
    assert "gpt-3.5" in breakdown
    assert breakdown["gpt-4"]["requests"] == 2
    assert breakdown["gpt-3.5"]["requests"] == 1


# ---------------------------------------------------------------------------
# Tests — optimize_prompt
# ---------------------------------------------------------------------------

def test_optimize_collapses_whitespace(mod):
    """optimize_prompt should collapse multiple spaces into one."""
    result = mod.optimize_prompt("hello    world   test")
    assert result == "hello world test"


def test_optimize_removes_filler(mod):
    """optimize_prompt should remove common filler phrases."""
    result = mod.optimize_prompt("I would like you to summarize this text")
    assert "I would like you to" not in result
    assert "summarize" in result


def test_optimize_truncates_to_budget(mod):
    """optimize_prompt should truncate to max_tokens * 4 characters."""
    long_prompt = "word " * 1000
    result = mod.optimize_prompt(long_prompt, max_tokens=10)
    assert len(result) <= 40  # 10 tokens * 4 chars


# ---------------------------------------------------------------------------
# Tests — select_model
# ---------------------------------------------------------------------------

def test_select_model_low_picks_fastest(mod):
    """Low complexity should pick the fastest model."""
    models = {
        "slow": {"context_window": 32768, "speed": 2, "quality": 10},
        "fast": {"context_window": 4096, "speed": 9, "quality": 3},
    }
    assert mod.select_model("low", models) == "fast"


def test_select_model_high_picks_best_quality(mod):
    """High complexity should pick the highest quality model."""
    models = {
        "fast": {"context_window": 4096, "speed": 9, "quality": 3},
        "smart": {"context_window": 32768, "speed": 2, "quality": 10},
    }
    assert mod.select_model("high", models) == "smart"


def test_select_model_medium_balances(mod):
    """Medium complexity should balance speed and quality."""
    models = {
        "fast": {"context_window": 4096, "speed": 9, "quality": 3},
        "balanced": {"context_window": 8192, "speed": 7, "quality": 8},
        "smart": {"context_window": 32768, "speed": 2, "quality": 10},
    }
    assert mod.select_model("medium", models) == "balanced"  # 7+8=15 > 12 > 12
