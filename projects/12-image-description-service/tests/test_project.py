"""Tests for Project 12: Image Description Service."""

import base64
import importlib.util
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
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
    with patch("requests.post"):
        return _load_module(SOLUTION_PATH)


# ── chat ──────────────────────────────────────────────────────


class TestChat:
    """Tests for the chat helper."""

    def test_chat_returns_content(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "A cat on a mat"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp):
            result = mod.chat("Describe this image", "base64data")
            assert result == "A cat on a mat"

    def test_chat_sends_image_in_payload(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "desc"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp) as mock_post:
            mod.chat("describe", "abc123")
            body = mock_post.call_args[1]["json"]
            assert body["messages"][0]["images"] == ["abc123"]
            assert body["model"] == mod.MODEL

    def test_chat_raises_on_http_error(self, mod):
        import requests as real_requests

        with patch.object(
            mod.requests, "post", side_effect=real_requests.ConnectionError("fail")
        ):
            with pytest.raises(Exception):
                mod.chat("prompt", "img")


# ── describe_image ────────────────────────────────────────────


class TestDescribeImage:
    """Tests for the describe_image function."""

    def test_encodes_bytes_to_base64(self, mod):
        image_bytes = b"fake image data"
        expected_b64 = base64.b64encode(image_bytes).decode("utf-8")

        with patch.object(mod, "chat", return_value="A photo") as mock_chat:
            result = mod.describe_image(image_bytes, "Describe this")
            mock_chat.assert_called_once_with("Describe this", expected_b64)
            assert result == "A photo"

    def test_describe_image_returns_string(self, mod):
        with patch.object(mod, "chat", return_value="Description here"):
            result = mod.describe_image(b"\x89PNG", "What is this?")
            assert isinstance(result, str)
            assert result == "Description here"

    def test_describe_image_empty_bytes(self, mod):
        expected_b64 = base64.b64encode(b"").decode("utf-8")
        with patch.object(mod, "chat", return_value="Empty") as mock_chat:
            mod.describe_image(b"", "describe")
            mock_chat.assert_called_once_with("describe", expected_b64)


# ── FastAPI endpoints ─────────────────────────────────────────


class TestEndpoints:
    """Tests for the FastAPI endpoints."""

    @pytest.fixture(autouse=True)
    def client(self, mod):
        from fastapi.testclient import TestClient
        self.client = TestClient(mod.app)

    def test_root_endpoint(self, mod):
        resp = self.client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "service" in data
        assert data["model"] == mod.MODEL

    def test_describe_endpoint_success(self, mod):
        with patch.object(mod, "describe_image", return_value="A sunset"):
            # Create a fake PNG image (minimal valid-looking bytes)
            fake_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
            resp = self.client.post(
                "/describe",
                files={"file": ("test.png", BytesIO(fake_image), "image/png")},
                data={"prompt": "Describe this"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["description"] == "A sunset"
            assert data["filename"] == "test.png"
            assert data["prompt"] == "Describe this"

    def test_describe_endpoint_rejects_non_image(self, mod):
        resp = self.client.post(
            "/describe",
            files={"file": ("doc.txt", BytesIO(b"hello"), "text/plain")},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data

    def test_describe_endpoint_default_prompt(self, mod):
        with patch.object(mod, "describe_image", return_value="A photo") as mock_desc:
            fake_image = b"\x89PNG" + b"\x00" * 50
            resp = self.client.post(
                "/describe",
                files={"file": ("img.png", BytesIO(fake_image), "image/png")},
            )
            assert resp.status_code == 200
            # Default prompt should be used
            call_args = mock_desc.call_args[0]
            assert "Describe this image" in call_args[1]
