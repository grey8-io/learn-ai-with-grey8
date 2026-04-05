"""Tests for Exercise 1 — Semantic Search Engine."""

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


# Mock embedding function for testing.
# Maps specific texts to known vectors for predictable results.
MOCK_VECTORS = {
    "python programming": [1.0, 0.0, 0.0],
    "machine learning": [0.0, 1.0, 0.0],
    "deep learning": [0.0, 0.9, 0.1],
    "cooking recipes": [0.0, 0.0, 1.0],
    "python": [0.9, 0.1, 0.0],
}


def mock_embedding(text: str) -> list[float]:
    """Return a known vector for test texts, or a simple hash-based one."""
    lower = text.lower().strip()
    if lower in MOCK_VECTORS:
        return MOCK_VECTORS[lower]
    # Fallback: simple deterministic embedding
    vec = [0.0, 0.0, 0.0]
    for i, ch in enumerate(lower):
        vec[i % 3] += ord(ch) / 1000.0
    mag = math.sqrt(sum(x * x for x in vec))
    if mag > 0:
        vec = [x / mag for x in vec]
    return vec


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    return _load_module(SOLUTION_PATH)


@pytest.fixture
def engine(mod):
    """Create a SemanticSearch engine with mock embeddings and indexed docs."""
    e = mod.SemanticSearch(mock_embedding)
    docs = [
        {"id": "d1", "text": "python programming", "metadata": {"topic": "code"}},
        {"id": "d2", "text": "machine learning", "metadata": {"topic": "ml"}},
        {"id": "d3", "text": "deep learning", "metadata": {"topic": "dl"}},
        {"id": "d4", "text": "cooking recipes", "metadata": {"topic": "food"}},
    ]
    e.index_documents(docs)
    return e


@pytest.fixture
def sample_docs():
    return [
        {"id": "d1", "text": "python programming", "metadata": {"topic": "code"}},
        {"id": "d2", "text": "machine learning", "metadata": {"topic": "ml"}},
        {"id": "d3", "text": "deep learning", "metadata": {"topic": "dl"}},
        {"id": "d4", "text": "cooking recipes", "metadata": {"topic": "food"}},
    ]


# ---------------------------------------------------------------------------
# Tests — __init__ and index_documents
# ---------------------------------------------------------------------------

def test_init_stores_embedding_fn(mod):
    """Should store the embedding function."""
    e = mod.SemanticSearch(mock_embedding)
    assert e.embedding_fn is mock_embedding


def test_index_documents_stores_all(engine):
    """Should index all provided documents."""
    assert len(engine._store) == 4


def test_index_documents_stores_text(engine):
    """Indexed documents should retain their text."""
    assert engine._store["d1"]["text"] == "python programming"


def test_index_documents_stores_metadata(engine):
    """Indexed documents should retain their metadata."""
    assert engine._store["d1"]["metadata"]["topic"] == "code"


def test_index_documents_stores_vectors(engine):
    """Indexed documents should have embedding vectors."""
    assert isinstance(engine._store["d1"]["vector"], list)
    assert len(engine._store["d1"]["vector"]) > 0


# ---------------------------------------------------------------------------
# Tests — search
# ---------------------------------------------------------------------------

def test_search_returns_list(engine):
    """Search should return a list."""
    results = engine.search("python")
    assert isinstance(results, list)


def test_search_result_keys(engine):
    """Each result should have id, score, text, and metadata."""
    results = engine.search("python", top_k=1)
    r = results[0]
    assert "id" in r
    assert "score" in r
    assert "text" in r
    assert "metadata" in r


def test_search_ranking(engine):
    """Most similar document should be ranked first."""
    results = engine.search("python", top_k=4)
    # "python" vector [0.9, 0.1, 0.0] is most similar to "python programming" [1.0, 0.0, 0.0]
    assert results[0]["id"] == "d1"


def test_search_top_k(engine):
    """Search should return at most top_k results."""
    results = engine.search("python", top_k=2)
    assert len(results) == 2


def test_search_scores_descending(engine):
    """Results should be sorted by score descending."""
    results = engine.search("python", top_k=4)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# Tests — keyword_search
# ---------------------------------------------------------------------------

def test_keyword_search_exact_match(mod, sample_docs):
    """Should find documents containing exact query terms."""
    e = mod.SemanticSearch(mock_embedding)
    results = e.keyword_search("learning", sample_docs)
    # "machine learning" and "deep learning" both contain "learning"
    top_ids = [r["id"] for r in results[:2]]
    assert "d2" in top_ids
    assert "d3" in top_ids


def test_keyword_search_no_match(mod, sample_docs):
    """Documents without query terms should have score 0."""
    e = mod.SemanticSearch(mock_embedding)
    results = e.keyword_search("xyz_nonexistent", sample_docs)
    assert all(r["score"] == 0 for r in results)


def test_keyword_search_returns_all_docs(mod, sample_docs):
    """Should return a result for every document."""
    e = mod.SemanticSearch(mock_embedding)
    results = e.keyword_search("python", sample_docs)
    assert len(results) == len(sample_docs)


def test_keyword_search_score_range(mod, sample_docs):
    """Scores should be between 0 and 1."""
    e = mod.SemanticSearch(mock_embedding)
    results = e.keyword_search("machine learning", sample_docs)
    for r in results:
        assert 0 <= r["score"] <= 1


# ---------------------------------------------------------------------------
# Tests — hybrid_search
# ---------------------------------------------------------------------------

def test_hybrid_search_returns_list(engine, sample_docs):
    """Hybrid search should return a list."""
    results = engine.hybrid_search("python", sample_docs)
    assert isinstance(results, list)


def test_hybrid_search_result_keys(engine, sample_docs):
    """Each hybrid result should have id and score."""
    results = engine.hybrid_search("python", sample_docs)
    assert "id" in results[0]
    assert "score" in results[0]


def test_hybrid_search_pure_semantic(engine, sample_docs):
    """With alpha=1.0, hybrid should equal semantic search."""
    hybrid = engine.hybrid_search("python", sample_docs, alpha=1.0)
    semantic = engine.search("python", top_k=len(sample_docs))
    assert hybrid[0]["id"] == semantic[0]["id"]


def test_hybrid_search_combines_scores(engine, sample_docs):
    """Hybrid scores should reflect both semantic and keyword components."""
    results = engine.hybrid_search("learning", sample_docs, alpha=0.5)
    # All results should have scores
    assert all(isinstance(r["score"], (int, float)) for r in results)


def test_hybrid_search_sorted(engine, sample_docs):
    """Hybrid results should be sorted by score descending."""
    results = engine.hybrid_search("python programming", sample_docs, alpha=0.5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)
