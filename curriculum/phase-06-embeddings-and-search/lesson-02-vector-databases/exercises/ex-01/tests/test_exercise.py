"""Tests for Exercise 1 — Simple Vector Store."""

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
def store(mod):
    """Create a fresh SimpleVectorStore for each test."""
    return mod.SimpleVectorStore()


# ---------------------------------------------------------------------------
# Tests — __init__ and count
# ---------------------------------------------------------------------------

def test_empty_store_count(store):
    """New store should have count of 0."""
    assert store.count() == 0


# ---------------------------------------------------------------------------
# Tests — add
# ---------------------------------------------------------------------------

def test_add_increases_count(store):
    """Adding a document should increase count."""
    store.add("doc1", [1, 0, 0])
    assert store.count() == 1


def test_add_multiple(store):
    """Adding multiple documents should increase count correctly."""
    store.add("doc1", [1, 0, 0])
    store.add("doc2", [0, 1, 0])
    store.add("doc3", [0, 0, 1])
    assert store.count() == 3


def test_add_with_metadata(store):
    """Should store metadata with the document."""
    store.add("doc1", [1, 0, 0], {"title": "Test"})
    results = store.search([1, 0, 0], top_k=1)
    assert results[0]["metadata"]["title"] == "Test"


def test_add_default_metadata(store):
    """Metadata should default to empty dict when not provided."""
    store.add("doc1", [1, 0, 0])
    results = store.search([1, 0, 0], top_k=1)
    assert results[0]["metadata"] == {}


# ---------------------------------------------------------------------------
# Tests — search
# ---------------------------------------------------------------------------

def test_search_returns_list(store):
    """Search should return a list."""
    store.add("doc1", [1, 0, 0])
    results = store.search([1, 0, 0])
    assert isinstance(results, list)


def test_search_result_keys(store):
    """Each search result should have id, score, and metadata."""
    store.add("doc1", [1, 0, 0])
    results = store.search([1, 0, 0])
    assert "id" in results[0]
    assert "score" in results[0]
    assert "metadata" in results[0]


def test_search_ranking(store):
    """Most similar document should be ranked first."""
    store.add("exact", [1, 0, 0])
    store.add("similar", [0.9, 0.1, 0])
    store.add("different", [0, 1, 0])
    results = store.search([1, 0, 0], top_k=3)
    assert results[0]["id"] == "exact"
    assert results[1]["id"] == "similar"
    assert results[2]["id"] == "different"


def test_search_top_k(store):
    """Search should return at most top_k results."""
    store.add("doc1", [1, 0, 0])
    store.add("doc2", [0, 1, 0])
    store.add("doc3", [0, 0, 1])
    results = store.search([1, 0, 0], top_k=2)
    assert len(results) == 2


def test_search_empty_store(store):
    """Searching an empty store should return empty list."""
    results = store.search([1, 0, 0])
    assert results == []


def test_search_score_range(store):
    """Scores should be between -1 and 1."""
    store.add("doc1", [1, 0, 0])
    store.add("doc2", [0, 1, 0])
    results = store.search([1, 0, 0])
    for r in results:
        assert -1.0 <= r["score"] <= 1.0


# ---------------------------------------------------------------------------
# Tests — delete
# ---------------------------------------------------------------------------

def test_delete_reduces_count(store):
    """Deleting a document should reduce count."""
    store.add("doc1", [1, 0, 0])
    store.add("doc2", [0, 1, 0])
    store.delete("doc1")
    assert store.count() == 1


def test_delete_removes_from_search(store):
    """Deleted documents should not appear in search results."""
    store.add("doc1", [1, 0, 0])
    store.add("doc2", [0, 1, 0])
    store.delete("doc1")
    results = store.search([1, 0, 0])
    ids = [r["id"] for r in results]
    assert "doc1" not in ids


def test_delete_nonexistent(store):
    """Deleting a non-existent ID should not raise an error."""
    store.add("doc1", [1, 0, 0])
    store.delete("nonexistent")  # Should not raise
    assert store.count() == 1
