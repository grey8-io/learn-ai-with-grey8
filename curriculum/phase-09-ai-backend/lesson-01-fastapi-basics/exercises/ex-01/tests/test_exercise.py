"""Tests for Exercise 1 — FastAPI AI Backend."""

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


@pytest.fixture(scope="module")
def client(mod):
    from fastapi.testclient import TestClient
    app = mod.create_app()
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests — Health endpoint
# ---------------------------------------------------------------------------

def test_health_returns_ok(client):
    """GET /health should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Tests — Predict endpoint
# ---------------------------------------------------------------------------

def test_predict_returns_response(client):
    """POST /predict should return a valid prediction response."""
    response = client.post("/predict", json={"text": "Hello world"})
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "confidence" in data
    assert "model" in data
    assert data["model"] == "default"


def test_predict_with_custom_model(client):
    """POST /predict should respect the model parameter."""
    response = client.post("/predict", json={"text": "Test", "model": "fast"})
    assert response.status_code == 200
    assert response.json()["model"] == "fast"


def test_predict_confidence_calculation(client):
    """Confidence should be min(len(text)/100, 1.0)."""
    short_text = "Hi"  # len=2, confidence=0.02
    response = client.post("/predict", json={"text": short_text})
    assert response.json()["confidence"] == pytest.approx(0.02)

    long_text = "x" * 200  # len=200, confidence=1.0 (capped)
    response = client.post("/predict", json={"text": long_text})
    assert response.json()["confidence"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Tests — Models endpoint
# ---------------------------------------------------------------------------

def test_models_returns_list(client):
    """GET /models should return a list of model names."""
    response = client.get("/models")
    assert response.status_code == 200
    models = response.json()
    assert isinstance(models, list)
    assert len(models) >= 1
    assert "default" in models


# ---------------------------------------------------------------------------
# Tests — Batch endpoint
# ---------------------------------------------------------------------------

def test_batch_processes_multiple_texts(client):
    """POST /batch should process all texts and return correct count."""
    texts = ["hello", "world", "test"]
    response = client.post("/batch", json={"texts": texts})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert len(data["results"]) == 3


def test_batch_empty_list(client):
    """POST /batch should handle an empty list."""
    response = client.post("/batch", json={"texts": []})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["results"] == []
