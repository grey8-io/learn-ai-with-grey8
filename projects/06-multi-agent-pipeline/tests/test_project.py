"""Tests for Project 06: Multi-Agent Pipeline."""

import importlib.util
import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call

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
        mock_resp.json.return_value = {"message": {"content": "ok"}}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp
        module = _load_module(SOLUTION_PATH)
    return module


# ---- Tests ----


class TestChat:
    """Tests for chat()."""

    def test_chat_sends_system_and_user(self, mod):
        """chat() should send both a system prompt and user message."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "response"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.chat("You are helpful.", "Hello")
            assert result == "response"

            payload = mock_post.call_args[1]["json"]
            messages = payload["messages"]
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "You are helpful."
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "Hello"

    def test_chat_returns_string(self, mod):
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "text"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.chat("sys", "usr")
            assert isinstance(result, str)


class TestAgent:
    """Tests for the Agent class."""

    def test_agent_has_name_and_prompt(self, mod):
        """Agent should store name and system_prompt."""
        agent = mod.Agent("TestAgent", "You are a test agent.")
        assert agent.name == "TestAgent"
        assert agent.system_prompt == "You are a test agent."

    def test_agent_run_calls_chat(self, mod):
        """Agent.run() should call chat() with the system prompt and input."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "agent output"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            agent = mod.Agent("Tester", "Be helpful")
            result = agent.run("input text")
            assert result == "agent output"

            payload = mock_post.call_args[1]["json"]
            assert payload["messages"][0]["content"] == "Be helpful"
            assert payload["messages"][1]["content"] == "input text"

    def test_agent_run_returns_string(self, mod):
        """Agent.run() should return a string."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "result"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            agent = mod.Agent("A", "sys")
            assert isinstance(agent.run("in"), str)


class TestCreateAgents:
    """Tests for create_agents()."""

    def test_returns_three_agents(self, mod):
        """create_agents() should return exactly 3 agents."""
        agents = mod.create_agents()
        assert len(agents) == 3

    def test_agents_are_agent_instances(self, mod):
        """Each item returned should be an Agent instance."""
        agents = mod.create_agents()
        for agent in agents:
            assert isinstance(agent, mod.Agent)

    def test_agent_names(self, mod):
        """Agents should be named Researcher, Writer, Reviewer."""
        agents = mod.create_agents()
        names = [a.name for a in agents]
        assert names == ["Researcher", "Writer", "Reviewer"]

    def test_agents_have_non_empty_prompts(self, mod):
        """Each agent should have a non-empty system prompt."""
        agents = mod.create_agents()
        for agent in agents:
            assert len(agent.system_prompt) > 20


class TestRunPipeline:
    """Tests for run_pipeline()."""

    def test_pipeline_chains_agents(self, mod):
        """run_pipeline() should pass output of each agent to the next."""
        call_count = 0
        responses = ["research notes", "draft article", "polished article"]

        with patch("requests.post") as mock_post:
            def side_effect(*args, **kwargs):
                nonlocal call_count
                mock_resp = MagicMock()
                mock_resp.json.return_value = {
                    "message": {"content": responses[call_count]}
                }
                mock_resp.raise_for_status = MagicMock()
                call_count += 1
                return mock_resp

            mock_post.side_effect = side_effect

            result = mod.run_pipeline("AI in healthcare")
            assert result == "polished article"
            assert call_count == 3

    def test_pipeline_returns_final_output(self, mod):
        """run_pipeline() should return the last agent's output."""
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"message": {"content": "final"}}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = mod.run_pipeline("topic")
            assert isinstance(result, str)
