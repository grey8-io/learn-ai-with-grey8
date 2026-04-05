"""Tests for Exercise 1 — Classify ML Problems."""

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
# Tests — Supervised
# ---------------------------------------------------------------------------

def test_supervised_predict(mod):
    """'predict' should indicate supervised learning."""
    result = mod.classify_ml_problem("Predict house prices based on features")
    assert result == "supervised"


def test_supervised_classify(mod):
    """'classify' should indicate supervised learning."""
    result = mod.classify_ml_problem("Classify emails as spam or not spam")
    assert result == "supervised"


def test_supervised_diagnose(mod):
    """'diagnose' should indicate supervised learning."""
    result = mod.classify_ml_problem("Diagnose diseases from medical images with known labels")
    assert result == "supervised"


# ---------------------------------------------------------------------------
# Tests — Unsupervised
# ---------------------------------------------------------------------------

def test_unsupervised_group(mod):
    """'group' should indicate unsupervised learning."""
    result = mod.classify_ml_problem("Group customers into segments based on purchasing behavior")
    assert result == "unsupervised"


def test_unsupervised_anomaly(mod):
    """'anomal' should indicate unsupervised learning."""
    result = mod.classify_ml_problem("Detect anomalies in network traffic data")
    assert result == "unsupervised"


def test_unsupervised_discover(mod):
    """'discover' should indicate unsupervised learning."""
    result = mod.classify_ml_problem("Discover topics in a collection of news articles")
    assert result == "unsupervised"


# ---------------------------------------------------------------------------
# Tests — Reinforcement
# ---------------------------------------------------------------------------

def test_reinforcement_robot(mod):
    """'robot' should indicate reinforcement learning."""
    result = mod.classify_ml_problem("Train a robot to navigate a maze")
    assert result == "reinforcement"


def test_reinforcement_play(mod):
    """'play' should indicate reinforcement learning."""
    result = mod.classify_ml_problem("Teach an AI to play chess by playing against itself")
    assert result == "reinforcement"


def test_reinforcement_optimize(mod):
    """'optimize' should indicate reinforcement learning."""
    result = mod.classify_ml_problem("Optimize traffic light timing to reduce congestion")
    assert result == "reinforcement"


# ---------------------------------------------------------------------------
# Tests — Edge cases
# ---------------------------------------------------------------------------

def test_case_insensitive(mod):
    """Classification should be case-insensitive."""
    result = mod.classify_ml_problem("PREDICT the weather for tomorrow")
    assert result == "supervised"


def test_unknown(mod):
    """Unrecognized descriptions should return 'unknown'."""
    result = mod.classify_ml_problem("Something completely unrelated to ML")
    assert result == "unknown"
