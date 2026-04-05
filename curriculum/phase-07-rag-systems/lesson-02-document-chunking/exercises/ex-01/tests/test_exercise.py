"""Tests for Exercise 1 — Document Chunking Utilities."""

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
# Tests — chunk_by_size
# ---------------------------------------------------------------------------

def test_chunk_by_size_basic(mod):
    """chunk_by_size should split text into fixed-size chunks."""
    text = "A" * 100
    chunks = mod.chunk_by_size(text, chunk_size=40, overlap=0)
    assert len(chunks) == 3
    assert chunks[0] == "A" * 40
    assert chunks[1] == "A" * 40
    assert chunks[2] == "A" * 20


def test_chunk_by_size_overlap(mod):
    """chunk_by_size should create overlapping chunks."""
    text = "abcdefghijklmnopqrst"  # 20 chars
    chunks = mod.chunk_by_size(text, chunk_size=10, overlap=3)
    # Chunk 0: 0-10, Chunk 1: 7-17, Chunk 2: 14-20
    assert chunks[0] == "abcdefghij"
    assert chunks[1] == "hijklmnopq"
    assert chunks[1][:3] == chunks[0][-3:]  # overlap check


def test_chunk_by_size_empty(mod):
    """chunk_by_size should return empty list for empty text."""
    assert mod.chunk_by_size("") == []


# ---------------------------------------------------------------------------
# Tests — chunk_by_sentences
# ---------------------------------------------------------------------------

def test_chunk_by_sentences_basic(mod):
    """chunk_by_sentences should group sentences correctly."""
    text = "First. Second. Third. Fourth. Fifth. Sixth."
    chunks = mod.chunk_by_sentences(text, sentences_per_chunk=2, overlap=0)
    assert len(chunks) == 3
    assert "First." in chunks[0]
    assert "Second." in chunks[0]
    assert "Third." in chunks[1]


def test_chunk_by_sentences_overlap(mod):
    """chunk_by_sentences should overlap sentences."""
    text = "One. Two. Three. Four."
    chunks = mod.chunk_by_sentences(text, sentences_per_chunk=2, overlap=1)
    # Chunk 0: One. Two.  Chunk 1: Two. Three.  Chunk 2: Three. Four.
    assert "Two." in chunks[0]
    assert "Two." in chunks[1]


def test_chunk_by_sentences_empty(mod):
    """chunk_by_sentences should return empty list for empty text."""
    assert mod.chunk_by_sentences("") == []


# ---------------------------------------------------------------------------
# Tests — chunk_by_paragraphs
# ---------------------------------------------------------------------------

def test_chunk_by_paragraphs_splits_on_double_newline(mod):
    """chunk_by_paragraphs should split on double newlines."""
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = mod.chunk_by_paragraphs(text, max_chunk_size=5000)
    # All paragraphs fit in one chunk
    assert len(chunks) == 1


def test_chunk_by_paragraphs_respects_max_size(mod):
    """chunk_by_paragraphs should split when max size is exceeded."""
    text = "A" * 50 + "\n\n" + "B" * 50 + "\n\n" + "C" * 50
    chunks = mod.chunk_by_paragraphs(text, max_chunk_size=60)
    assert len(chunks) == 3
    assert "A" * 50 in chunks[0]
    assert "B" * 50 in chunks[1]


def test_chunk_by_paragraphs_empty(mod):
    """chunk_by_paragraphs should return empty list for empty text."""
    assert mod.chunk_by_paragraphs("") == []


# ---------------------------------------------------------------------------
# Tests — chunk_markdown
# ---------------------------------------------------------------------------

def test_chunk_markdown_splits_on_headings(mod):
    """chunk_markdown should split on markdown headings."""
    text = "# Heading One\n\nContent one.\n\n## Heading Two\n\nContent two."
    chunks = mod.chunk_markdown(text, max_chunk_size=5000)
    assert len(chunks) == 2
    assert "Heading One" in chunks[0]
    assert "Content one" in chunks[0]
    assert "Heading Two" in chunks[1]


def test_chunk_markdown_empty(mod):
    """chunk_markdown should return empty list for empty text."""
    assert mod.chunk_markdown("") == []


# ---------------------------------------------------------------------------
# Tests — add_chunk_metadata
# ---------------------------------------------------------------------------

def test_add_chunk_metadata_structure(mod):
    """add_chunk_metadata should return correct metadata structure."""
    chunks = ["Hello world", "Another chunk"]
    result = mod.add_chunk_metadata(chunks, source="test.txt")
    assert len(result) == 2
    assert result[0]["text"] == "Hello world"
    assert result[0]["index"] == 0
    assert result[0]["source"] == "test.txt"
    assert result[0]["char_count"] == 11
    assert result[0]["word_count"] == 2
    assert result[1]["index"] == 1
