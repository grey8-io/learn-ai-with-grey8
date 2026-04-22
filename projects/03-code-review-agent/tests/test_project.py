"""Tests for Project 03: Code Review Agent."""

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
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "Review feedback"}}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp
        module = _load_module(SOLUTION_PATH)
    return module


# ---- Tests ----


class TestReadFile:
    """Tests for read_file()."""

    def test_read_existing_py_file(self, mod, tmp_path):
        """read_file() should return contents of a .py file."""
        py_file = tmp_path / "sample.py"
        py_file.write_text("print('hello')", encoding="utf-8")
        result = mod.read_file(py_file)
        assert result == "print('hello')"

    def test_read_nonexistent_file(self, mod, tmp_path):
        """read_file() should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            mod.read_file(tmp_path / "nonexistent.py")

    def test_read_non_python_file(self, mod, tmp_path):
        """read_file() should raise ValueError for non-.py files."""
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("some text", encoding="utf-8")
        with pytest.raises(ValueError, match="Not a Python file"):
            mod.read_file(txt_file)

    def test_read_file_returns_string(self, mod, tmp_path):
        """read_file() should always return a string."""
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        result = mod.read_file(py_file)
        assert isinstance(result, str)


class TestChat:
    """Tests for chat()."""

    def test_chat_returns_response(self, mod):
        """chat() should return the LLM response content."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "message": {"content": "Looks good!"}
            }
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.chat("Review this code")
            assert result == "Looks good!"

    def test_chat_sends_correct_model(self, mod):
        """chat() should use the configured MODEL."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "ok"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            mod.chat("test")
            payload = mock_post.call_args[1]["json"]
            assert payload["model"] == mod.MODEL


class TestReviewCode:
    """Tests for review_code()."""

    def test_review_code_calls_chat(self, mod):
        """review_code() should call chat() with a prompt containing the code."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "message": {"content": "## Issues\n- None"}
            }
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.review_code("def foo(): pass", "test.py")
            assert isinstance(result, str)
            # Verify the code was included in the prompt
            payload = mock_post.call_args[1]["json"]
            prompt = payload["messages"][0]["content"]
            assert "def foo(): pass" in prompt

    def test_review_code_uses_review_prompt_template(self, mod):
        """review_code() should use the REVIEW_PROMPT template."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "feedback"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            mod.review_code("x = 1", "t.py")
            payload = mock_post.call_args[1]["json"]
            prompt = payload["messages"][0]["content"]
            assert "code reviewer" in prompt.lower() or "review" in prompt.lower()


class TestReviewPrompt:
    """Tests for the REVIEW_PROMPT template."""

    def test_prompt_contains_placeholder(self, mod):
        """REVIEW_PROMPT should contain {code} placeholder."""
        assert "{code}" in mod.REVIEW_PROMPT

    def test_prompt_requests_structured_output(self, mod):
        """REVIEW_PROMPT should ask for Issues and Suggestions sections."""
        assert "Issues" in mod.REVIEW_PROMPT
        assert "Suggestions" in mod.REVIEW_PROMPT


class TestReviewFile:
    """Tests for review_file()."""

    def test_review_file_prints_feedback(self, mod, tmp_path, capsys):
        """review_file() should print the review header and feedback."""
        py_file = tmp_path / "sample.py"
        py_file.write_text("def foo():\n    return 42\n", encoding="utf-8")

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "message": {"content": "## Issues\n- No issues"}
            }
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            mod.review_file(py_file)
            captured = capsys.readouterr()
            assert "sample.py" in captured.out

    def test_review_file_skips_empty(self, mod, tmp_path, capsys):
        """review_file() should skip empty files."""
        py_file = tmp_path / "empty.py"
        py_file.write_text("", encoding="utf-8")
        mod.review_file(py_file)
        captured = capsys.readouterr()
        assert "empty file" in captured.out.lower() or "skipping" in captured.out.lower()
