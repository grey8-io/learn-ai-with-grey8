"""Tests for Exercise 1 — Multi-Agent Orchestrator."""

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


@pytest.fixture
def agents(mod):
    """Create a set of test agents."""
    return {
        "planner": mod.AgentRole("planner", "You plan tasks.", ["plan", "organize"]),
        "writer": mod.AgentRole("writer", "You write content.", ["write", "document"]),
        "reviewer": mod.AgentRole("reviewer", "You review work.", ["review", "check"]),
    }


def make_counter_generate():
    """Create a generate_fn that counts calls."""
    state = {"count": 0}

    def generate(prompt):
        state["count"] += 1
        return f"Response {state['count']}"

    return generate, state


# ---------------------------------------------------------------------------
# Tests — AgentRole
# ---------------------------------------------------------------------------

def test_agent_role_attributes(mod):
    """AgentRole should store name, system_prompt, and capabilities."""
    role = mod.AgentRole("test", "Be helpful.", ["help", "assist"])
    assert role.name == "test"
    assert role.system_prompt == "Be helpful."
    assert role.capabilities == ["help", "assist"]


# ---------------------------------------------------------------------------
# Tests — Message
# ---------------------------------------------------------------------------

def test_message_attributes(mod):
    """Message should store all fields with defaults."""
    msg = mod.Message("agent_a", "agent_b", "Hello", "task")
    assert msg.from_agent == "agent_a"
    assert msg.to_agent == "agent_b"
    assert msg.content == "Hello"
    assert msg.message_type == "task"


def test_message_default_type(mod):
    """Message should default message_type to 'task'."""
    msg = mod.Message("a", "b", "content")
    assert msg.message_type == "task"


# ---------------------------------------------------------------------------
# Tests — route_task
# ---------------------------------------------------------------------------

def test_route_task_matches(mod, agents):
    """route_task should match task to agent by capability keyword."""
    gen, _ = make_counter_generate()
    orch = mod.Orchestrator(agents=agents, generate_fn=gen)
    assert orch.route_task("Please review my code") == "reviewer"


def test_route_task_no_match(mod, agents):
    """route_task should return None when no agent matches."""
    gen, _ = make_counter_generate()
    orch = mod.Orchestrator(agents=agents, generate_fn=gen)
    assert orch.route_task("Do something random xyz") is None


# ---------------------------------------------------------------------------
# Tests — run_pipeline
# ---------------------------------------------------------------------------

def test_run_pipeline_executes_all_agents(mod, agents):
    """run_pipeline should call generate_fn once per agent in the pipeline."""
    gen, state = make_counter_generate()
    orch = mod.Orchestrator(agents=agents, generate_fn=gen)
    result = orch.run_pipeline("Build a feature", ["planner", "writer", "reviewer"])
    assert state["count"] == 3
    assert result == "Response 3"  # Final output from last agent


def test_run_pipeline_creates_messages(mod, agents):
    """run_pipeline should create one message per agent."""
    gen, _ = make_counter_generate()
    orch = mod.Orchestrator(agents=agents, generate_fn=gen)
    orch.run_pipeline("Task", ["planner", "writer"])
    results = orch.collect_results()
    assert len(results) == 2
    assert results[0]["from"] == "planner"
    assert results[1]["from"] == "writer"


# ---------------------------------------------------------------------------
# Tests — run_debate
# ---------------------------------------------------------------------------

def test_run_debate_correct_rounds(mod, agents):
    """run_debate should generate responses for each agent in each round."""
    gen, state = make_counter_generate()
    orch = mod.Orchestrator(agents=agents, generate_fn=gen)
    result = orch.run_debate("Is Python good?", ["writer", "reviewer"], rounds=2)
    # 2 agents * 2 rounds = 4 calls
    assert state["count"] == 4


def test_run_debate_returns_last_response(mod, agents):
    """run_debate should return the final response."""
    gen, state = make_counter_generate()
    orch = mod.Orchestrator(agents=agents, generate_fn=gen)
    result = orch.run_debate("Question?", ["writer", "reviewer"], rounds=1)
    assert result == "Response 2"  # Last response in round 1


# ---------------------------------------------------------------------------
# Tests — collect_results
# ---------------------------------------------------------------------------

def test_collect_results_format(mod, agents):
    """collect_results should return dicts with correct keys."""
    gen, _ = make_counter_generate()
    orch = mod.Orchestrator(agents=agents, generate_fn=gen)
    orch.run_pipeline("Task", ["planner"])
    results = orch.collect_results()
    assert len(results) == 1
    msg = results[0]
    assert "from" in msg
    assert "to" in msg
    assert "content" in msg
    assert "type" in msg
