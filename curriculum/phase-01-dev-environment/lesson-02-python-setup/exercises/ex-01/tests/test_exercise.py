"""Tests for Exercise 1 — Python Hello World with Functions."""

import importlib.util
import os
import sys
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
# Tests
# ---------------------------------------------------------------------------

def test_bootcamp_name(mod):
    """bootcamp_name should be the correct string."""
    assert hasattr(mod, "bootcamp_name"), "Variable 'bootcamp_name' is not defined"
    assert mod.bootcamp_name == "Learn AI With Grey8"


def test_version(mod):
    """version should be the integer 1."""
    assert hasattr(mod, "version"), "Variable 'version' is not defined"
    assert mod.version == 1
    assert isinstance(mod.version, int), "version should be an integer, not a string"


def test_welcome_message(mod):
    """welcome_message should combine bootcamp_name and version."""
    assert hasattr(mod, "welcome_message"), "Variable 'welcome_message' is not defined"
    assert mod.welcome_message == "Welcome to Learn AI With Grey8 v1!"


def test_greet_function_exists(mod):
    """A callable function named 'greet' should exist."""
    assert hasattr(mod, "greet"), "Function 'greet' is not defined"
    assert callable(mod.greet), "'greet' should be a function"


def test_greet_returns_correct_string(mod):
    """greet('Alice') should return the expected greeting."""
    result = mod.greet("Alice")
    assert result == "Hello, Alice! Let's build something amazing."


def test_greet_with_different_name(mod):
    """greet should work with any name."""
    result = mod.greet("World")
    assert result == "Hello, World! Let's build something amazing."
