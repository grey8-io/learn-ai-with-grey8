"""Tests for Project 04: Semantic Search Engine."""

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
        mock_collection.count.return_value = 0
        mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
        module = _load_module(SOLUTION_PATH)
    return module


# ---- Tests ----


class TestAddDocument:
    """Tests for add_document()."""

    def test_add_document_basic(self, mod):
        """add_document() should add a document to the collection."""
        mod.collection = MagicMock()
        mod.add_document("doc1", "Hello world")
        mod.collection.add.assert_called_once()
        call_kwargs = mod.collection.add.call_args[1]
        assert call_kwargs["ids"] == ["doc1"]
        assert call_kwargs["documents"] == ["Hello world"]

    def test_add_document_with_metadata(self, mod):
        """add_document() should pass metadata when provided."""
        mod.collection = MagicMock()
        mod.add_document("doc2", "Text here", metadata={"source": "test"})
        call_kwargs = mod.collection.add.call_args[1]
        assert call_kwargs["metadatas"] == [{"source": "test"}]

    def test_add_document_without_metadata(self, mod):
        """add_document() should not pass metadatas when metadata is None."""
        mod.collection = MagicMock()
        mod.add_document("doc3", "No meta")
        call_kwargs = mod.collection.add.call_args[1]
        assert "metadatas" not in call_kwargs


class TestSearch:
    """Tests for search()."""

    def test_search_empty_collection(self, mod):
        """search() should return empty list when collection is empty."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 0
        results = mod.search("anything")
        assert results == []

    def test_search_returns_results(self, mod):
        """search() should return a list of dicts with id, text, distance."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 2
        mod.collection.query.return_value = {
            "ids": [["doc1", "doc2"]],
            "documents": [["First doc", "Second doc"]],
            "distances": [[0.1, 0.5]],
        }
        results = mod.search("query text", n_results=2)
        assert len(results) == 2
        assert results[0]["id"] == "doc1"
        assert results[0]["text"] == "First doc"
        assert results[0]["distance"] == 0.1
        assert results[1]["id"] == "doc2"

    def test_search_clamps_n_results(self, mod):
        """search() should clamp n_results to the collection size."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 2
        mod.collection.query.return_value = {
            "ids": [["doc1", "doc2"]],
            "documents": [["A", "B"]],
            "distances": [[0.1, 0.2]],
        }
        mod.search("test", n_results=100)
        call_kwargs = mod.collection.query.call_args[1]
        assert call_kwargs["n_results"] == 2


class TestFlaskRoutes:
    """Tests for Flask API routes."""

    @pytest.fixture()
    def client(self, mod):
        """Create a Flask test client."""
        mod.app.config["TESTING"] = True
        with mod.app.test_client() as c:
            yield c

    def test_health_endpoint(self, mod, client):
        """GET /health should return status ok and document count."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 5
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["documents"] == 5

    def test_add_route_success(self, mod, client):
        """POST /add with valid data should return 201."""
        mod.collection = MagicMock()
        resp = client.post("/add", json={"id": "test1", "text": "Hello"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["id"] == "test1"

    def test_add_route_missing_fields(self, mod, client):
        """POST /add without required fields should return 400."""
        resp = client.post("/add", json={"id": "test1"})
        assert resp.status_code == 400

    def test_search_route_success(self, mod, client):
        """POST /search with valid query should return results."""
        mod.collection = MagicMock()
        mod.collection.count.return_value = 1
        mod.collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["content"]],
            "distances": [[0.2]],
        }
        resp = client.post("/search", json={"query": "test"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data
        assert len(data["results"]) == 1

    def test_search_route_missing_query(self, mod, client):
        """POST /search without query should return 400."""
        resp = client.post("/search", json={})
        assert resp.status_code == 400
