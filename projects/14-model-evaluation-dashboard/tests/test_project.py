"""Tests for Project 14: Model Evaluation Dashboard."""

import importlib.util
import os
import sys
import time
import pytest
from unittest.mock import patch, MagicMock

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "reference", "main.py"
)


def _load_module(path: str):
    spec = importlib.util.spec_from_file_location("student_main", path)
    mod = importlib.util.module_from_spec(spec)
    # Streamlit and pandas need to be available but we mock streamlit calls
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    with patch("requests.post"):
        return _load_module(SOLUTION_PATH)


# ── chat ──────────────────────────────────────────────────────


class TestChat:
    """Tests for the chat helper with timing metrics."""

    def test_chat_returns_dict_with_metrics(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "The answer is 42"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp):
            result = mod.chat("What is the answer?")
            assert "response" in result
            assert "latency_ms" in result
            assert "response_length" in result
            assert result["response"] == "The answer is 42"
            assert result["response_length"] == len("The answer is 42")

    def test_chat_latency_is_positive(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "ok"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp):
            result = mod.chat("test")
            assert result["latency_ms"] >= 0

    def test_chat_accepts_model_parameter(self, mod):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "ok"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(mod.requests, "post", return_value=mock_resp) as mock_post:
            mod.chat("test", model="custom-model")
            body = mock_post.call_args[1]["json"]
            assert body["model"] == "custom-model"

    def test_chat_raises_on_failure(self, mod):
        import requests as real_requests

        with patch.object(
            mod.requests, "post", side_effect=real_requests.ConnectionError("down")
        ):
            with pytest.raises(Exception):
                mod.chat("test")


# ── run_benchmark ─────────────────────────────────────────────


class TestRunBenchmark:
    """Tests for the run_benchmark function."""

    def test_run_benchmark_returns_dataframe(self, mod):
        import pandas as pd

        mock_result = {
            "response": "answer",
            "latency_ms": 100.0,
            "response_length": 6,
        }
        with patch.object(mod, "chat", return_value=mock_result):
            df = mod.run_benchmark(["prompt 1", "prompt 2"])
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2

    def test_run_benchmark_includes_prompt_column(self, mod):
        mock_result = {
            "response": "ans",
            "latency_ms": 50.0,
            "response_length": 3,
        }
        with patch.object(mod, "chat", return_value=mock_result):
            df = mod.run_benchmark(["What is AI?"])
            assert "prompt" in df.columns
            assert df.iloc[0]["prompt"] == "What is AI?"

    def test_run_benchmark_has_metric_columns(self, mod):
        mock_result = {
            "response": "test",
            "latency_ms": 75.5,
            "response_length": 4,
        }
        with patch.object(mod, "chat", return_value=mock_result):
            df = mod.run_benchmark(["p1"])
            assert "latency_ms" in df.columns
            assert "response_length" in df.columns
            assert "response" in df.columns

    def test_run_benchmark_empty_prompts(self, mod):
        import pandas as pd

        with patch.object(mod, "chat") as mock_chat:
            df = mod.run_benchmark([])
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 0
            mock_chat.assert_not_called()

    def test_run_benchmark_passes_model(self, mod):
        mock_result = {
            "response": "ok",
            "latency_ms": 10.0,
            "response_length": 2,
        }
        with patch.object(mod, "chat", return_value=mock_result) as mock_chat:
            mod.run_benchmark(["p1"], model="tiny-model")
            mock_chat.assert_called_once_with("p1", "tiny-model")


# ── DEFAULT_PROMPTS ───────────────────────────────────────────


class TestDefaults:
    """Tests for module-level defaults."""

    def test_default_prompts_exist(self, mod):
        assert hasattr(mod, "DEFAULT_PROMPTS")
        assert isinstance(mod.DEFAULT_PROMPTS, list)
        assert len(mod.DEFAULT_PROMPTS) >= 3

    def test_default_prompts_are_strings(self, mod):
        for prompt in mod.DEFAULT_PROMPTS:
            assert isinstance(prompt, str)
            assert len(prompt) > 0
