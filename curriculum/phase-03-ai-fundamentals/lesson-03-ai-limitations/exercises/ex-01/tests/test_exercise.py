"""Tests for Exercise 1 — AI Fact Checker."""

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


@pytest.fixture
def known_facts():
    return {
        "capital_of_france": "The capital of France is Paris",
        "boiling_point": "Water boils at 100 degrees Celsius",
        "speed_of_light": "The speed of light is approximately 300000 km per second",
    }


# ---------------------------------------------------------------------------
# Tests — Verified claims
# ---------------------------------------------------------------------------

def test_verified_exact_match(mod, known_facts):
    """A claim matching a known fact should be verified."""
    results = mod.fact_checker(["The capital of France is Paris"], known_facts)
    assert len(results) == 1
    assert results[0]["status"] == "verified"


def test_verified_case_insensitive(mod, known_facts):
    """Verification should be case-insensitive."""
    results = mod.fact_checker(["the capital of france is paris"], known_facts)
    assert results[0]["status"] == "verified"


def test_verified_has_reason(mod, known_facts):
    """Verified results should include a reason with the matching fact."""
    results = mod.fact_checker(["The capital of France is Paris"], known_facts)
    assert "Matches known fact" in results[0]["reason"]


# ---------------------------------------------------------------------------
# Tests — Contradicted claims
# ---------------------------------------------------------------------------

def test_contradicted_wrong_answer(mod, known_facts):
    """A claim about a known topic with wrong info should be contradicted."""
    results = mod.fact_checker(["The capital of France is London"], known_facts)
    assert results[0]["status"] == "contradicted"


def test_contradicted_has_reason(mod, known_facts):
    """Contradicted results should include a reason with the correct fact."""
    results = mod.fact_checker(["The capital of France is London"], known_facts)
    assert "Contradicts known fact" in results[0]["reason"]


# ---------------------------------------------------------------------------
# Tests — Unverified claims
# ---------------------------------------------------------------------------

def test_unverified_no_matching_topic(mod, known_facts):
    """A claim about an unknown topic should be unverified."""
    results = mod.fact_checker(["Elephants can fly"], known_facts)
    assert results[0]["status"] == "unverified"


def test_unverified_has_reason(mod, known_facts):
    """Unverified results should explain that no facts are available."""
    results = mod.fact_checker(["Elephants can fly"], known_facts)
    assert "No matching facts" in results[0]["reason"]


# ---------------------------------------------------------------------------
# Tests — Multiple claims
# ---------------------------------------------------------------------------

def test_multiple_claims(mod, known_facts):
    """Should handle multiple claims at once."""
    claims = [
        "The capital of France is Paris",
        "The capital of France is London",
        "Elephants can fly",
    ]
    results = mod.fact_checker(claims, known_facts)
    assert len(results) == 3
    assert results[0]["status"] == "verified"
    assert results[1]["status"] == "contradicted"
    assert results[2]["status"] == "unverified"


def test_result_structure(mod, known_facts):
    """Each result should have claim, status, and reason keys."""
    results = mod.fact_checker(["test claim"], known_facts)
    assert "claim" in results[0]
    assert "status" in results[0]
    assert "reason" in results[0]


def test_empty_claims(mod, known_facts):
    """Empty claims list should return empty results."""
    results = mod.fact_checker([], known_facts)
    assert results == []
