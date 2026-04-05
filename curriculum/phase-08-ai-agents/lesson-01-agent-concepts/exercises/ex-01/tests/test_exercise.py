"""Tests for Exercise 1 — Simple Agent Framework."""

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


# ---------------------------------------------------------------------------
# Tests — Tool class
# ---------------------------------------------------------------------------

def test_tool_attributes(mod):
    """Tool should store name, description, and function."""
    fn = lambda x: x
    tool = mod.Tool(name="test", description="A test tool", function=fn)
    assert tool.name == "test"
    assert tool.description == "A test tool"
    assert tool.function is fn


# ---------------------------------------------------------------------------
# Tests — AgentState class
# ---------------------------------------------------------------------------

def test_agent_state_defaults(mod):
    """AgentState should initialize with empty lists and iteration 0."""
    state = mod.AgentState()
    assert state.messages == []
    assert state.tool_results == []
    assert state.iteration == 0


# ---------------------------------------------------------------------------
# Tests — parse_action
# ---------------------------------------------------------------------------

def test_parse_action_found(mod):
    """parse_action should extract tool name and args."""
    agent = mod.SimpleAgent(tools=[], generate_fn=lambda x: x)
    result = agent.parse_action("Let me check. ACTION: search(Python tutorials)")
    assert result is not None
    assert result["tool"] == "search"
    assert result["args"] == "Python tutorials"


def test_parse_action_not_found(mod):
    """parse_action should return None when no action in response."""
    agent = mod.SimpleAgent(tools=[], generate_fn=lambda x: x)
    result = agent.parse_action("The answer is 42.")
    assert result is None


# ---------------------------------------------------------------------------
# Tests — execute_tool
# ---------------------------------------------------------------------------

def test_execute_tool_success(mod):
    """execute_tool should call the matching tool and return its result."""
    tool = mod.Tool("upper", "Uppercases text", lambda x: x.upper())
    agent = mod.SimpleAgent(tools=[tool], generate_fn=lambda x: x)
    result = agent.execute_tool("upper", "hello")
    assert result == "HELLO"


def test_execute_tool_not_found(mod):
    """execute_tool should return an error message for unknown tools."""
    agent = mod.SimpleAgent(tools=[], generate_fn=lambda x: x)
    result = agent.execute_tool("missing", "args")
    assert "Error" in result
    assert "missing" in result


# ---------------------------------------------------------------------------
# Tests — run (agent loop)
# ---------------------------------------------------------------------------

def test_run_direct_answer(mod):
    """run should return immediately if no action in first response."""
    agent = mod.SimpleAgent(
        tools=[],
        generate_fn=lambda prompt: "The answer is 42.",
    )
    result = agent.run("What is the answer?")
    assert result["answer"] == "The answer is 42."
    assert result["iterations"] == 0


def test_run_with_tool_use(mod):
    """run should execute tools and continue the loop."""
    call_count = {"n": 0}

    def mock_generate(prompt):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return "ACTION: calculator(5)"
        return "The answer is 10."

    tool = mod.Tool("calculator", "Doubles input", lambda x: str(int(x) * 2))
    agent = mod.SimpleAgent(tools=[tool], generate_fn=mock_generate)
    result = agent.run("Double 5")
    assert result["answer"] == "The answer is 10."
    assert result["iterations"] == 1


def test_run_max_iterations(mod):
    """run should stop after max_iterations."""
    agent = mod.SimpleAgent(
        tools=[mod.Tool("noop", "Does nothing", lambda x: "ok")],
        generate_fn=lambda prompt: "ACTION: noop(x)",
        max_iterations=3,
    )
    result = agent.run("Loop forever")
    assert result["iterations"] == 3
    assert "Max iterations" in result["answer"]
