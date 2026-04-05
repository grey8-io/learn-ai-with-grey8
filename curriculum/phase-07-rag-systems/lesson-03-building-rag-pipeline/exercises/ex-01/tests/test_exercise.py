"""Tests for Exercise 1 — Document QA System."""

import importlib.util
import os
import tempfile
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


def mock_embed(text):
    """Simple deterministic embedding based on character frequencies."""
    return [text.lower().count(c) / max(len(text), 1) for c in "abcdefghij"]


def mock_generate(prompt):
    """Mock generator that echoes part of the prompt."""
    return "Generated answer about the topic."


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    return _load_module(SOLUTION_PATH)


@pytest.fixture
def temp_files():
    """Create temporary text files for testing."""
    tmpdir = tempfile.mkdtemp()
    files = []
    contents = [
        "Python is a programming language created by Guido van Rossum.",
        "Machine learning is a subset of artificial intelligence.",
        "RAG stands for Retrieval-Augmented Generation.",
    ]
    for i, content in enumerate(contents):
        path = os.path.join(tmpdir, f"doc{i}.txt")
        with open(path, "w") as f:
            f.write(content)
        files.append(path)
    return files, tmpdir


# ---------------------------------------------------------------------------
# Tests — __init__
# ---------------------------------------------------------------------------

def test_init_stores_functions(mod):
    """__init__ should store embedding_fn and generate_fn."""
    qa = mod.DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)
    assert qa.embedding_fn is mock_embed
    assert qa.generate_fn is mock_generate


def test_init_empty_store(mod):
    """__init__ should initialize an empty store."""
    qa = mod.DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)
    assert qa.store == []


# ---------------------------------------------------------------------------
# Tests — load_documents
# ---------------------------------------------------------------------------

def test_load_documents(mod, temp_files):
    """load_documents should read files and return path/content dicts."""
    files, _ = temp_files
    qa = mod.DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)
    docs = qa.load_documents(files)
    assert len(docs) == 3
    assert docs[0]["path"] == files[0]
    assert "Python" in docs[0]["content"]


def test_load_documents_skips_missing(mod):
    """load_documents should skip files that don't exist."""
    qa = mod.DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)
    docs = qa.load_documents(["/nonexistent/file.txt"])
    assert len(docs) == 0


# ---------------------------------------------------------------------------
# Tests — process_documents
# ---------------------------------------------------------------------------

def test_process_documents_stores_chunks(mod):
    """process_documents should store embedded chunks."""
    qa = mod.DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)
    documents = [{"path": "test.txt", "content": "Hello world. This is a test."}]
    count = qa.process_documents(documents, chunk_size=500)
    assert count == 1
    assert len(qa.store) == 1
    assert qa.store[0]["text"] == "Hello world. This is a test."
    assert qa.store[0]["source"] == "test.txt"
    assert isinstance(qa.store[0]["embedding"], list)


def test_process_documents_chunks_large_content(mod):
    """process_documents should create multiple chunks for large content."""
    qa = mod.DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)
    documents = [{"path": "big.txt", "content": "A" * 1200}]
    count = qa.process_documents(documents, chunk_size=500)
    assert count == 3  # 500 + 500 + 200


# ---------------------------------------------------------------------------
# Tests — answer
# ---------------------------------------------------------------------------

def test_answer_returns_dict(mod):
    """answer should return a dict with answer, sources, and confidence."""
    qa = mod.DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)
    qa.store = [
        {"embedding": mock_embed("python"), "text": "Python is great.", "source": "a.txt"},
        {"embedding": mock_embed("java"), "text": "Java is verbose.", "source": "b.txt"},
    ]
    result = qa.answer("Tell me about Python")
    assert "answer" in result
    assert "sources" in result
    assert "confidence" in result
    assert isinstance(result["sources"], list)
    assert isinstance(result["confidence"], float)


# ---------------------------------------------------------------------------
# Tests — evaluate_answer
# ---------------------------------------------------------------------------

def test_evaluate_answer_all_found(mod):
    """evaluate_answer should return score 1.0 when all keywords found."""
    qa = mod.DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)
    result = qa.evaluate_answer("Python is a great language", ["python", "language"])
    assert result["score"] == 1.0
    assert len(result["found"]) == 2
    assert len(result["missing"]) == 0


def test_evaluate_answer_partial(mod):
    """evaluate_answer should return partial score for partial matches."""
    qa = mod.DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)
    result = qa.evaluate_answer("Python is great", ["python", "java"])
    assert result["score"] == 0.5
    assert "python" in result["found"]
    assert "java" in result["missing"]
