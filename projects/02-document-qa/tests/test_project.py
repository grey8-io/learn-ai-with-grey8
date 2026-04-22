"""Tests for Project 02: Document QA."""

import importlib.util
import os
import sys
import pytest
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
        mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
        module = _load_module(SOLUTION_PATH)
    return module


# ---- Tests ----


class TestChunkText:
    """Tests for chunk_text()."""

    def test_basic_chunking(self, mod):
        """Should split text into chunks of the specified size."""
        text = "a" * 1000
        chunks = mod.chunk_text(text, chunk_size=500)
        assert len(chunks) == 2
        assert all(len(c) == 500 for c in chunks)

    def test_chunking_with_remainder(self, mod):
        """Should handle text that doesn't divide evenly."""
        text = "a" * 750
        chunks = mod.chunk_text(text, chunk_size=500)
        assert len(chunks) == 2
        assert len(chunks[0]) == 500
        assert len(chunks[1]) == 250

    def test_empty_text(self, mod):
        """Should return empty list for empty/whitespace text."""
        assert mod.chunk_text("") == []
        assert mod.chunk_text("   ") == []

    def test_small_text(self, mod):
        """Text smaller than chunk_size should produce one chunk."""
        chunks = mod.chunk_text("short text", chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == "short text"

    def test_custom_chunk_size(self, mod):
        """Should respect a custom chunk_size parameter."""
        text = "abcdefghij" * 10  # 100 chars
        chunks = mod.chunk_text(text, chunk_size=25)
        assert len(chunks) == 4


class TestReadFile:
    """Tests for read_file()."""

    def test_read_txt_file(self, mod, tmp_path):
        """Should read text content from a .txt file."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Hello, world!", encoding="utf-8")
        result = mod.read_file(str(txt_file))
        assert result == "Hello, world!"

    def test_read_pdf_file(self, mod, tmp_path):
        """Should read text content from a .pdf file via PyPDF2."""
        pdf_path = str(tmp_path / "test.pdf")
        with patch("PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "PDF content"
            mock_reader.return_value.pages = [mock_page]

            result = mod.read_file(pdf_path)
            assert result == "PDF content"


class TestChat:
    """Tests for chat()."""

    def test_chat_returns_llm_response(self, mod):
        """chat() should return the LLM's response text."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "Answer here"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.chat("What is Python?")
            assert result == "Answer here"

    def test_chat_sends_stream_false(self, mod):
        """chat() should send stream=False to get a complete response."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "ok"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            mod.chat("test")
            payload = mock_post.call_args[1]["json"]
            assert payload["stream"] is False


class TestIngestDocument:
    """Tests for ingest_document()."""

    def test_ingest_adds_chunks_to_collection(self, mod, tmp_path):
        """ingest_document() should chunk file content and add to ChromaDB."""
        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("a" * 1200, encoding="utf-8")

        mod.collection = MagicMock()

        count = mod.ingest_document(str(txt_file))
        # 1200 chars / 500 chunk_size = 3 chunks (500+500+200)
        assert count == 3
        mod.collection.add.assert_called_once()
        call_kwargs = mod.collection.add.call_args[1]
        assert len(call_kwargs["documents"]) == 3
        assert len(call_kwargs["ids"]) == 3

    def test_ingest_empty_file_returns_zero(self, mod, tmp_path):
        """ingest_document() should return 0 for an empty file."""
        txt_file = tmp_path / "empty.txt"
        txt_file.write_text("", encoding="utf-8")

        mod.collection = MagicMock()
        count = mod.ingest_document(str(txt_file))
        assert count == 0


class TestQuery:
    """Tests for query()."""

    def test_query_empty_collection(self, mod):
        """query() should return a message when no documents are ingested."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 0

        result = mod.query("What is Python?")
        assert "no documents" in result.lower() or "ingest" in result.lower()

    def test_query_builds_rag_prompt(self, mod):
        """query() should retrieve chunks and call chat with a RAG prompt."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 3
        mod.collection.query.return_value = {
            "documents": [["chunk1", "chunk2", "chunk3"]],
        }

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "RAG answer"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.query("question?")
            assert result == "RAG answer"
            # Verify the prompt contains context
            payload = mock_post.call_args[1]["json"]
            prompt_text = payload["messages"][0]["content"]
            assert "chunk1" in prompt_text
