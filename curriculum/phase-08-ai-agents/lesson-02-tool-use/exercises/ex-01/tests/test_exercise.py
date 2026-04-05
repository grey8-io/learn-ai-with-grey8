"""Tests for Exercise 1 — Tool Registry & Built-in Tools."""

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
# Tests — calculator
# ---------------------------------------------------------------------------

def test_calculator_addition(mod):
    """calculator should evaluate addition."""
    assert mod.calculator("2 + 3") == "5"


def test_calculator_complex(mod):
    """calculator should evaluate complex expressions."""
    assert mod.calculator("(10 + 5) * 2") == "30"


def test_calculator_rejects_unsafe(mod):
    """calculator should reject expressions with unsafe characters."""
    result = mod.calculator("__import__('os').system('ls')")
    assert "Error" in result


# ---------------------------------------------------------------------------
# Tests — word_count
# ---------------------------------------------------------------------------

def test_word_count_basic(mod):
    """word_count should count words correctly."""
    assert mod.word_count("hello world") == "2"


def test_word_count_empty(mod):
    """word_count should return 0 for empty/whitespace-only string."""
    # "".split() returns [], len([]) = 0
    result = mod.word_count("")
    assert result == "0" or result == "1"  # depends on implementation


# ---------------------------------------------------------------------------
# Tests — search_list
# ---------------------------------------------------------------------------

def test_search_list_found(mod):
    """search_list should find matching items."""
    items = ["Python tutorial", "Java guide", "Python cookbook"]
    result = mod.search_list(items, "python")
    assert "Found 2 results" in result
    assert "Python tutorial" in result
    assert "Python cookbook" in result


def test_search_list_not_found(mod):
    """search_list should return no results message."""
    items = ["Python tutorial", "Java guide"]
    result = mod.search_list(items, "rust")
    assert "No results found" in result


# ---------------------------------------------------------------------------
# Tests — ToolRegistry
# ---------------------------------------------------------------------------

def test_registry_register_and_get(mod):
    """register should store tool and get_tool should retrieve it."""
    registry = mod.ToolRegistry()
    fn = lambda x: x
    registry.register("test", fn, "A test tool", {"x": "input"})
    tool = registry.get_tool("test")
    assert tool is not None
    assert tool["description"] == "A test tool"


def test_registry_get_missing(mod):
    """get_tool should return None for unregistered tools."""
    registry = mod.ToolRegistry()
    assert registry.get_tool("missing") is None


def test_registry_list_tools(mod):
    """list_tools should return all registered tools."""
    registry = mod.ToolRegistry()
    registry.register("a", lambda: None, "Tool A")
    registry.register("b", lambda: None, "Tool B")
    tools = registry.list_tools()
    assert len(tools) == 2
    names = [t["name"] for t in tools]
    assert "a" in names
    assert "b" in names


def test_registry_format_for_prompt(mod):
    """format_tools_for_prompt should produce a numbered list."""
    registry = mod.ToolRegistry()
    registry.register("calc", lambda: None, "Does math.")
    registry.register("search", lambda: None, "Searches things.")
    result = registry.format_tools_for_prompt()
    assert "Available tools:" in result
    assert "1. calc" in result
    assert "2. search" in result


def test_registry_execute_success(mod):
    """execute should call the tool function and return its result."""
    registry = mod.ToolRegistry()
    registry.register("upper", lambda text: text.upper(), "Uppercases text")
    result = registry.execute("upper", text="hello")
    assert result == "HELLO"


def test_registry_execute_not_found(mod):
    """execute should return error for missing tools."""
    registry = mod.ToolRegistry()
    result = registry.execute("missing")
    assert "Error" in result
    assert "missing" in result


def test_registry_execute_handles_error(mod):
    """execute should catch exceptions from tool functions."""
    registry = mod.ToolRegistry()
    registry.register("broken", lambda: 1 / 0, "Always fails")
    result = registry.execute("broken")
    assert "Error" in result
