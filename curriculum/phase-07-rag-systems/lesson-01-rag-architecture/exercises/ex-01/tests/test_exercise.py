"""Tests for Exercise 1 — RAG Pipeline."""

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
# Mock helpers
# ---------------------------------------------------------------------------

def make_retriever(docs):
    """Create a mock retriever that returns the given docs."""
    def retriever(query, top_k=3):
        return docs[:top_k]
    return retriever


def make_generator(response):
    """Create a mock generator that returns a fixed response."""
    def generator(prompt):
        return response
    return generator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    return _load_module(SOLUTION_PATH)


# ---------------------------------------------------------------------------
# Tests — __init__
# ---------------------------------------------------------------------------

def test_stores_retriever(mod):
    """__init__ should store the retriever callable."""
    r = make_retriever([])
    g = make_generator("")
    pipeline = mod.RAGPipeline(retriever=r, generator=g)
    assert pipeline.retriever is r


def test_stores_generator(mod):
    """__init__ should store the generator callable."""
    r = make_retriever([])
    g = make_generator("")
    pipeline = mod.RAGPipeline(retriever=r, generator=g)
    assert pipeline.generator is g


# ---------------------------------------------------------------------------
# Tests — build_context
# ---------------------------------------------------------------------------

def test_build_context_joins_documents(mod):
    """build_context should join documents with separator."""
    pipeline = mod.RAGPipeline(make_retriever([]), make_generator(""))
    docs = ["Doc one.", "Doc two.", "Doc three."]
    result = pipeline.build_context(docs)
    assert "Doc one." in result
    assert "Doc two." in result
    assert "Doc three." in result
    assert "\n\n---\n\n" in result


def test_build_context_respects_max_chars(mod):
    """build_context should stop adding documents when max_chars is exceeded."""
    pipeline = mod.RAGPipeline(make_retriever([]), make_generator(""))
    docs = ["A" * 100, "B" * 100, "C" * 100]
    result = pipeline.build_context(docs, max_chars=150)
    assert "A" * 100 in result
    assert "B" * 100 not in result


def test_build_context_empty_list(mod):
    """build_context with empty list should return empty string."""
    pipeline = mod.RAGPipeline(make_retriever([]), make_generator(""))
    result = pipeline.build_context([])
    assert result == ""


# ---------------------------------------------------------------------------
# Tests — build_prompt
# ---------------------------------------------------------------------------

def test_build_prompt_format(mod):
    """build_prompt should return the correct format."""
    pipeline = mod.RAGPipeline(make_retriever([]), make_generator(""))
    result = pipeline.build_prompt("What is AI?", "AI is artificial intelligence.")
    assert result == "Given the following context:\nAI is artificial intelligence.\n\nAnswer: What is AI?"


# ---------------------------------------------------------------------------
# Tests — query
# ---------------------------------------------------------------------------

def test_query_returns_answer(mod):
    """query should return the generated answer string."""
    docs = ["Python is a language.", "Python is popular."]
    pipeline = mod.RAGPipeline(
        retriever=make_retriever(docs),
        generator=make_generator("Python is great."),
    )
    result = pipeline.query("What is Python?")
    assert result == "Python is great."


def test_query_passes_top_k(mod):
    """query should pass top_k to the retriever."""
    called_with = {}

    def tracking_retriever(query, top_k=3):
        called_with["top_k"] = top_k
        return ["doc"]

    pipeline = mod.RAGPipeline(
        retriever=tracking_retriever,
        generator=make_generator("answer"),
    )
    pipeline.query("question", top_k=5)
    assert called_with["top_k"] == 5


# ---------------------------------------------------------------------------
# Tests — query_with_sources
# ---------------------------------------------------------------------------

def test_query_with_sources_returns_dict(mod):
    """query_with_sources should return a dict with answer, sources, and query."""
    docs = ["Source one.", "Source two."]
    pipeline = mod.RAGPipeline(
        retriever=make_retriever(docs),
        generator=make_generator("The answer."),
    )
    result = pipeline.query_with_sources("My question")
    assert isinstance(result, dict)
    assert result["answer"] == "The answer."
    assert result["sources"] == docs
    assert result["query"] == "My question"
