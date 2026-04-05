"""Tests for Project 13: AI Testing Framework."""

import importlib.util
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

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
        mock_resp.json.return_value = {"message": {"content": "analysis result"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp):
            result = mod.chat([{"role": "user", "content": "analyze"}])
            assert result == "analysis result"

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
            assert body["stream"] is False

    def test_chat_raises_on_failure(self, mod):
        import requests as real_requests

        with patch.object(
            mod.requests, "post", side_effect=real_requests.ConnectionError("down")
        ):
            with pytest.raises(Exception):
                mod.chat([{"role": "user", "content": "hi"}])


# ── analyze_code ──────────────────────────────────────────────


class TestAnalyzeCode:
    """Tests for the analyze_code function."""

    def test_analyze_code_sends_source(self, mod):
        source = "def add(a, b):\n    return a + b"
        with patch.object(mod, "chat", return_value="Found function add") as mock_chat:
            result = mod.analyze_code(source)
            assert result == "Found function add"
            sent_messages = mock_chat.call_args[0][0]
            assert source in sent_messages[1]["content"]

    def test_analyze_code_system_prompt_asks_for_analysis(self, mod):
        with patch.object(mod, "chat", return_value="analysis") as mock_chat:
            mod.analyze_code("x = 1")
            sent_messages = mock_chat.call_args[0][0]
            system = sent_messages[0]["content"].lower()
            assert "analyzer" in system or "analyz" in system


# ── generate_tests ────────────────────────────────────────────


class TestGenerateTests:
    """Tests for the generate_tests function."""

    def test_generate_tests_returns_code(self, mod):
        with patch.object(mod, "chat", return_value="def test_add():\n    assert add(1,2)==3"):
            result = mod.generate_tests("def add(a,b): return a+b", "function add")
            assert "def test_add" in result

    def test_generate_tests_strips_markdown_fences(self, mod):
        fenced = "```python\ndef test_foo():\n    pass\n```"
        with patch.object(mod, "chat", return_value=fenced):
            result = mod.generate_tests("def foo(): pass", "function foo")
            assert "```" not in result
            assert "def test_foo" in result

    def test_generate_tests_includes_source_and_analysis(self, mod):
        with patch.object(mod, "chat", return_value="test code") as mock_chat:
            mod.generate_tests("source_code_here", "analysis_here")
            sent_messages = mock_chat.call_args[0][0]
            user_msg = sent_messages[1]["content"]
            assert "source_code_here" in user_msg
            assert "analysis_here" in user_msg

    def test_generate_tests_system_prompt_mentions_pytest(self, mod):
        with patch.object(mod, "chat", return_value="tests") as mock_chat:
            mod.generate_tests("code", "analysis")
            sent_messages = mock_chat.call_args[0][0]
            system = sent_messages[0]["content"].lower()
            assert "pytest" in system


# ── main (integration) ───────────────────────────────────────


class TestMain:
    """Tests for the main entry point."""

    def test_main_exits_without_args(self, mod):
        with patch.object(sys, "argv", ["main.py"]):
            with pytest.raises(SystemExit) as exc_info:
                mod.main()
            assert exc_info.value.code == 1

    def test_main_exits_with_nonexistent_file(self, mod, tmp_path):
        fake_file = str(tmp_path / "nonexistent.py")
        with patch.object(sys, "argv", ["main.py", fake_file]):
            with pytest.raises(SystemExit) as exc_info:
                mod.main()
            assert exc_info.value.code == 1

    def test_main_full_pipeline(self, mod, tmp_path):
        # Create a source file
        source_file = tmp_path / "example.py"
        source_file.write_text("def greet(name):\n    return f'Hello {name}'", encoding="utf-8")

        with patch.object(sys, "argv", ["main.py", str(source_file)]):
            with patch.object(mod, "analyze_code", return_value="function greet"):
                with patch.object(mod, "generate_tests", return_value="def test_greet(): pass"):
                    mod.main()

        # Check that the test file was written
        test_file = Path(f"test_{source_file.name}")
        assert test_file.exists() or (tmp_path / f"test_{source_file.name}").exists()
        # Clean up if in cwd
        if test_file.exists():
            test_file.unlink()
