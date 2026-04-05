"""Tests for Exercise 1 — Fetch and Save JSON."""

import importlib.util
import json
import os
import tempfile
from unittest.mock import MagicMock, patch
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
def sample_data():
    return {"userId": 1, "id": 1, "title": "Test todo", "completed": False}


# ---------------------------------------------------------------------------
# Tests — fetch_and_save
# ---------------------------------------------------------------------------

def test_fetch_and_save_returns_data(mod, sample_data):
    """fetch_and_save should return the parsed JSON data."""
    mock_response = MagicMock()
    mock_response.json.return_value = sample_data
    mock_response.raise_for_status = MagicMock()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        filepath = tmp.name

    try:
        with patch("httpx.get", return_value=mock_response) as mock_get:
            result = mod.fetch_and_save("https://example.com/data", filepath)

        assert result == sample_data
        mock_get.assert_called_once_with("https://example.com/data", timeout=10)
    finally:
        os.unlink(filepath)


def test_fetch_and_save_writes_file(mod, sample_data):
    """fetch_and_save should write valid JSON to the file."""
    mock_response = MagicMock()
    mock_response.json.return_value = sample_data
    mock_response.raise_for_status = MagicMock()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        filepath = tmp.name

    try:
        with patch("httpx.get", return_value=mock_response):
            mod.fetch_and_save("https://example.com/data", filepath)

        with open(filepath, "r") as f:
            saved = json.load(f)
        assert saved == sample_data
    finally:
        os.unlink(filepath)


def test_fetch_and_save_calls_raise_for_status(mod, sample_data):
    """fetch_and_save should call raise_for_status() to check for errors."""
    mock_response = MagicMock()
    mock_response.json.return_value = sample_data

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        filepath = tmp.name

    try:
        with patch("httpx.get", return_value=mock_response):
            mod.fetch_and_save("https://example.com/data", filepath)

        mock_response.raise_for_status.assert_called_once()
    finally:
        os.unlink(filepath)


# ---------------------------------------------------------------------------
# Tests — load_json
# ---------------------------------------------------------------------------

def test_load_json_reads_file(mod, sample_data):
    """load_json should parse and return JSON from a file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        json.dump(sample_data, tmp)
        filepath = tmp.name

    try:
        result = mod.load_json(filepath)
        assert result == sample_data
    finally:
        os.unlink(filepath)


def test_load_json_file_not_found(mod):
    """load_json should return None when the file doesn't exist."""
    result = mod.load_json("/nonexistent/path/data.json")
    assert result is None


def test_load_json_returns_dict(mod, sample_data):
    """load_json should return a dict."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        json.dump(sample_data, tmp)
        filepath = tmp.name

    try:
        result = mod.load_json(filepath)
        assert isinstance(result, dict)
    finally:
        os.unlink(filepath)
