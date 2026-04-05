"""Tests for Exercise 1 — Embedding Utilities."""

import importlib.util
import math
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
# Tests — cosine_similarity
# ---------------------------------------------------------------------------

def test_cosine_identical_vectors(mod):
    """Identical vectors should have cosine similarity of 1.0."""
    result = mod.cosine_similarity([1, 2, 3], [1, 2, 3])
    assert abs(result - 1.0) < 1e-6


def test_cosine_orthogonal_vectors(mod):
    """Orthogonal vectors should have cosine similarity of 0.0."""
    result = mod.cosine_similarity([1, 0, 0], [0, 1, 0])
    assert abs(result - 0.0) < 1e-6


def test_cosine_opposite_vectors(mod):
    """Opposite vectors should have cosine similarity of -1.0."""
    result = mod.cosine_similarity([1, 0], [-1, 0])
    assert abs(result - (-1.0)) < 1e-6


def test_cosine_similar_vectors(mod):
    """Similar vectors should have high cosine similarity."""
    result = mod.cosine_similarity([1, 2, 3], [1, 2, 4])
    assert result > 0.9


def test_cosine_zero_vector(mod):
    """Zero vector should return 0.0."""
    result = mod.cosine_similarity([0, 0, 0], [1, 2, 3])
    assert result == 0.0


# ---------------------------------------------------------------------------
# Tests — euclidean_distance
# ---------------------------------------------------------------------------

def test_euclidean_same_vector(mod):
    """Distance between identical vectors should be 0."""
    result = mod.euclidean_distance([1, 2, 3], [1, 2, 3])
    assert abs(result) < 1e-6


def test_euclidean_known_distance(mod):
    """3-4-5 triangle: distance between (0,0) and (3,4) is 5."""
    result = mod.euclidean_distance([0, 0], [3, 4])
    assert abs(result - 5.0) < 1e-6


def test_euclidean_unit_vectors(mod):
    """Distance between orthogonal unit vectors should be sqrt(2)."""
    result = mod.euclidean_distance([1, 0], [0, 1])
    assert abs(result - math.sqrt(2)) < 1e-6


def test_euclidean_positive(mod):
    """Distance should always be non-negative."""
    result = mod.euclidean_distance([5, 5], [1, 1])
    assert result > 0


# ---------------------------------------------------------------------------
# Tests — most_similar
# ---------------------------------------------------------------------------

def test_most_similar_exact_match(mod):
    """Should return the label of the exact matching vector."""
    vectors = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    labels = ["x", "y", "z"]
    result = mod.most_similar([1, 0, 0], vectors, labels)
    assert result == "x"


def test_most_similar_closest(mod):
    """Should return the label of the closest vector."""
    vectors = [[1, 0, 0], [0, 1, 0], [0.9, 0.1, 0]]
    labels = ["pure-x", "pure-y", "mostly-x"]
    result = mod.most_similar([0.8, 0.2, 0], vectors, labels)
    assert result == "mostly-x"


def test_most_similar_single_vector(mod):
    """Should work with a single vector."""
    result = mod.most_similar([1, 0], [[0, 1]], ["only"])
    assert result == "only"


# ---------------------------------------------------------------------------
# Tests — normalize_vector
# ---------------------------------------------------------------------------

def test_normalize_known_vector(mod):
    """Normalizing [3, 4] should give [0.6, 0.8]."""
    result = mod.normalize_vector([3.0, 4.0])
    assert abs(result[0] - 0.6) < 1e-6
    assert abs(result[1] - 0.8) < 1e-6


def test_normalize_magnitude_is_one(mod):
    """Normalized vector should have magnitude 1."""
    result = mod.normalize_vector([2, 3, 6])
    magnitude = math.sqrt(sum(x * x for x in result))
    assert abs(magnitude - 1.0) < 1e-6


def test_normalize_zero_vector(mod):
    """Zero vector should be returned unchanged."""
    result = mod.normalize_vector([0.0, 0.0, 0.0])
    assert result == [0.0, 0.0, 0.0]


def test_normalize_already_unit(mod):
    """A unit vector should remain unchanged after normalization."""
    result = mod.normalize_vector([1.0, 0.0, 0.0])
    assert abs(result[0] - 1.0) < 1e-6
    assert abs(result[1] - 0.0) < 1e-6
    assert abs(result[2] - 0.0) < 1e-6
