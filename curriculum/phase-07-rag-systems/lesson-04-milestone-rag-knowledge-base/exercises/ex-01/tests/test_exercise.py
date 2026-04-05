"""Tests for Project 05: RAG Knowledge Base."""

import importlib.util
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "reference", "main.py"
)


def _load_module(path: str):
    spec = importlib.util.spec_from_file_location("student_main", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    with patch("chromadb.Client") as mock_chroma, \
         patch("requests.post") as mock_post:
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
        module = _load_module(SOLUTION_PATH)
    return module


# ---- Tests ----


class TestChunkText:
    """Tests for chunk_text()."""

    def test_basic_chunking(self, mod):
        """Should split text into chunks of the specified size."""
        text = "x" * 1500
        chunks = mod.chunk_text(text, chunk_size=500)
        assert len(chunks) == 3

    def test_empty_text(self, mod):
        """Should return empty list for blank text."""
        assert mod.chunk_text("") == []

    def test_whitespace_only_chunks_filtered(self, mod):
        """Chunks that are only whitespace should be filtered out."""
        # 500 spaces + 500 chars of 'a'
        text = " " * 500 + "a" * 500
        chunks = mod.chunk_text(text, chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == "a" * 500

    def test_single_chunk(self, mod):
        """Short text should produce exactly one chunk."""
        chunks = mod.chunk_text("short", chunk_size=500)
        assert len(chunks) == 1


class TestIngestFolder:
    """Tests for ingest_folder()."""

    def test_ingest_md_files(self, mod, tmp_path):
        """ingest_folder() should read .md files and add chunks to ChromaDB."""
        (tmp_path / "note1.md").write_text("a" * 600, encoding="utf-8")
        (tmp_path / "note2.md").write_text("b" * 300, encoding="utf-8")

        mod.collection = MagicMock()
        files, chunks = mod.ingest_folder(str(tmp_path))

        assert files == 2
        # note1: 600/500 = 2 chunks, note2: 300/500 = 1 chunk => total 3
        assert chunks == 3
        assert mod.collection.add.call_count == 2

    def test_ingest_empty_folder(self, mod, tmp_path):
        """ingest_folder() should return (0, 0) for folder with no .md files."""
        mod.collection = MagicMock()
        files, chunks = mod.ingest_folder(str(tmp_path))
        assert files == 0
        assert chunks == 0

    def test_ingest_skips_empty_files(self, mod, tmp_path):
        """ingest_folder() should skip .md files with no content."""
        (tmp_path / "empty.md").write_text("", encoding="utf-8")
        (tmp_path / "real.md").write_text("content here", encoding="utf-8")

        mod.collection = MagicMock()
        files, chunks = mod.ingest_folder(str(tmp_path))
        assert files == 1
        assert chunks == 1

    def test_ingest_creates_correct_ids(self, mod, tmp_path):
        """Chunk IDs should contain the filename and index."""
        (tmp_path / "notes.md").write_text("hello world", encoding="utf-8")

        mod.collection = MagicMock()
        mod.ingest_folder(str(tmp_path))

        call_kwargs = mod.collection.add.call_args[1]
        assert call_kwargs["ids"] == ["notes.md_chunk_0"]

    def test_ingest_stores_source_metadata(self, mod, tmp_path):
        """Each chunk should have source metadata with the filename."""
        (tmp_path / "doc.md").write_text("some text", encoding="utf-8")

        mod.collection = MagicMock()
        mod.ingest_folder(str(tmp_path))

        call_kwargs = mod.collection.add.call_args[1]
        assert call_kwargs["metadatas"] == [{"source": "doc.md"}]


class TestAsk:
    """Tests for ask()."""

    def test_ask_empty_collection(self, mod):
        """ask() should return an informative message when no docs are loaded."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 0
        result = mod.ask("What is Python?")
        assert "no documents" in result.lower() or "ingest" in result.lower()

    def test_ask_with_documents(self, mod):
        """ask() should query ChromaDB and return an LLM-generated answer."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 3
        mod.collection.query.return_value = {
            "documents": [["Python is a language", "It was created in 1991"]],
            "metadatas": [
                [{"source": "python.md"}, {"source": "history.md"}]
            ],
        }

        with patch("student_main.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "message": {"content": "Python is a programming language."}
            }
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.ask("What is Python?", n_results=2)
            assert result == "Python is a programming language."

    def test_ask_includes_source_in_prompt(self, mod):
        """ask() should include source attribution in the RAG prompt."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 1
        mod.collection.query.return_value = {
            "documents": [["chunk content"]],
            "metadatas": [[{"source": "notes.md"}]],
        }

        with patch("student_main.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "answer"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            mod.ask("question?", n_results=1)
            payload = mock_post.call_args[1]["json"]
            prompt = payload["messages"][0]["content"]
            assert "notes.md" in prompt


class TestChat:
    """Tests for chat()."""

    def test_chat_returns_string(self, mod):
        with patch("student_main.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "reply"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.chat("hello")
            assert isinstance(result, str)
            assert result == "reply"
