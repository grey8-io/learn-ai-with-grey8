"""Tests for Project 15: Full-Stack AI SaaS."""

import importlib.util
import os
import sys
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from io import BytesIO

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
    with patch("requests.post"), patch("chromadb.Client") as mock_chroma:
        # Set up a mock ChromaDB collection
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
        return _load_module(SOLUTION_PATH)


# ── chat ──────────────────────────────────────────────────────


class TestChat:
    """Tests for the chat helper."""

    def test_chat_returns_content(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "Hello!"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp):
            result = mod.chat([{"role": "user", "content": "hi"}])
            assert result == "Hello!"

    def test_chat_sends_correct_payload(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "ok"}}
        mock_resp.raise_for_status = MagicMock()

        messages = [{"role": "user", "content": "test"}]
        with patch.object(mod.requests, "post", return_value=mock_resp) as mock_post:
            mod.chat(messages)
            body = mock_post.call_args[1]["json"]
            assert body["model"] == mod.MODEL
            assert body["messages"] == messages


# ── add_to_knowledge_base ────────────────────────────────────


class TestAddToKnowledgeBase:
    """Tests for the add_to_knowledge_base function."""

    def test_splits_text_into_paragraphs(self, mod):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        original_collection = mod.collection
        mod.collection = mock_collection

        try:
            text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
            mod.add_to_knowledge_base(text, "doc1")
            mock_collection.add.assert_called_once()
            call_kwargs = mock_collection.add.call_args[1]
            assert len(call_kwargs["documents"]) == 3
            assert call_kwargs["documents"][0] == "Paragraph one."
            assert call_kwargs["documents"][1] == "Paragraph two."
        finally:
            mod.collection = original_collection

    def test_splits_large_chunks(self, mod):
        mock_collection = MagicMock()
        original_collection = mod.collection
        mod.collection = mock_collection

        try:
            # Create a single paragraph longer than 500 chars
            long_text = "word " * 200  # ~1000 chars, no double newlines
            mod.add_to_knowledge_base(long_text, "longdoc")
            mock_collection.add.assert_called_once()
            call_kwargs = mock_collection.add.call_args[1]
            # Should be split into multiple chunks
            assert len(call_kwargs["documents"]) >= 2
            for chunk in call_kwargs["documents"]:
                assert len(chunk) <= 600  # allowing some slack
        finally:
            mod.collection = original_collection

    def test_skips_empty_text(self, mod):
        mock_collection = MagicMock()
        original_collection = mod.collection
        mod.collection = mock_collection

        try:
            mod.add_to_knowledge_base("", "empty")
            mock_collection.add.assert_not_called()
        finally:
            mod.collection = original_collection

    def test_generates_correct_ids(self, mod):
        mock_collection = MagicMock()
        original_collection = mod.collection
        mod.collection = mock_collection

        try:
            text = "Chunk A.\n\nChunk B."
            mod.add_to_knowledge_base(text, "mydoc")
            call_kwargs = mock_collection.add.call_args[1]
            assert call_kwargs["ids"] == ["mydoc_chunk_0", "mydoc_chunk_1"]
        finally:
            mod.collection = original_collection


# ── search_knowledge_base ─────────────────────────────────────


class TestSearchKnowledgeBase:
    """Tests for the search_knowledge_base function."""

    def test_returns_empty_when_collection_empty(self, mod):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        original_collection = mod.collection
        mod.collection = mock_collection

        try:
            result = mod.search_knowledge_base("query")
            assert result == []
        finally:
            mod.collection = original_collection

    def test_returns_documents_from_query(self, mod):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 5
        mock_collection.query.return_value = {
            "documents": [["chunk 1", "chunk 2"]],
        }
        original_collection = mod.collection
        mod.collection = mock_collection

        try:
            result = mod.search_knowledge_base("search term", n_results=2)
            assert result == ["chunk 1", "chunk 2"]
            mock_collection.query.assert_called_once()
        finally:
            mod.collection = original_collection

    def test_clamps_n_results_to_collection_size(self, mod):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 2
        mock_collection.query.return_value = {"documents": [["a", "b"]]}
        original_collection = mod.collection
        mod.collection = mock_collection

        try:
            mod.search_knowledge_base("query", n_results=100)
            call_kwargs = mock_collection.query.call_args[1]
            assert call_kwargs["n_results"] == 2
        finally:
            mod.collection = original_collection


# ── chat_with_rag ─────────────────────────────────────────────


class TestChatWithRag:
    """Tests for the chat_with_rag function."""

    def test_with_context(self, mod):
        with patch.object(mod, "search_knowledge_base", return_value=["relevant info"]):
            with patch.object(mod, "chat", return_value="Based on context...") as mock_chat:
                result = mod.chat_with_rag("What is X?")
                assert result == "Based on context..."
                sent_messages = mock_chat.call_args[0][0]
                system_msg = sent_messages[0]["content"]
                assert "relevant info" in system_msg

    def test_without_context(self, mod):
        with patch.object(mod, "search_knowledge_base", return_value=[]):
            with patch.object(mod, "chat", return_value="I don't have context") as mock_chat:
                result = mod.chat_with_rag("What is X?")
                assert result == "I don't have context"
                sent_messages = mock_chat.call_args[0][0]
                system_msg = sent_messages[0]["content"]
                assert "empty" in system_msg.lower()

    def test_user_message_passed_through(self, mod):
        with patch.object(mod, "search_knowledge_base", return_value=[]):
            with patch.object(mod, "chat", return_value="answer") as mock_chat:
                mod.chat_with_rag("my specific question")
                sent_messages = mock_chat.call_args[0][0]
                user_msg = sent_messages[1]["content"]
                assert user_msg == "my specific question"


# ── FastAPI endpoints ─────────────────────────────────────────


class TestEndpoints:
    """Tests for the FastAPI endpoints."""

    @pytest.fixture(autouse=True)
    def client(self, mod):
        from fastapi.testclient import TestClient
        self.client = TestClient(mod.app)

    def test_chat_endpoint_success(self, mod):
        with patch.object(mod, "chat_with_rag", return_value="AI response"):
            resp = self.client.post("/chat", data={"message": "Hello"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["response"] == "AI response"
            assert data["message"] == "Hello"

    def test_upload_rejects_non_txt(self, mod):
        resp = self.client.post(
            "/upload",
            files={"file": ("data.csv", BytesIO(b"a,b,c"), "text/csv")},
        )
        assert resp.status_code == 400

    def test_upload_rejects_empty_file(self, mod):
        resp = self.client.post(
            "/upload",
            files={"file": ("notes.txt", BytesIO(b""), "text/plain")},
        )
        assert resp.status_code == 400

    def test_search_endpoint(self, mod):
        with patch.object(mod, "search_knowledge_base", return_value=["result1"]):
            resp = self.client.get("/search", params={"query": "test"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["query"] == "test"
            assert data["results"] == ["result1"]
            assert data["count"] == 1
