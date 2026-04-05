"""Tests for Exercise 1 — Variables, Types & Functions."""

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
# Tests — celsius_to_fahrenheit
# ---------------------------------------------------------------------------

def test_celsius_to_fahrenheit_freezing(mod):
    """0°C should equal 32°F."""
    assert mod.celsius_to_fahrenheit(0) == 32


def test_celsius_to_fahrenheit_boiling(mod):
    """100°C should equal 212°F."""
    assert mod.celsius_to_fahrenheit(100) == 212


def test_celsius_to_fahrenheit_negative(mod):
    """-40°C should equal -40°F (the crossover point)."""
    assert mod.celsius_to_fahrenheit(-40) == -40


def test_celsius_to_fahrenheit_body_temp(mod):
    """37°C should equal 98.6°F."""
    result = mod.celsius_to_fahrenheit(37)
    assert abs(result - 98.6) < 0.01


# ---------------------------------------------------------------------------
# Tests — is_palindrome
# ---------------------------------------------------------------------------

def test_is_palindrome_simple(mod):
    """'racecar' is a palindrome."""
    assert mod.is_palindrome("racecar") is True


def test_is_palindrome_case_insensitive(mod):
    """'Racecar' should still be detected as a palindrome."""
    assert mod.is_palindrome("Racecar") is True


def test_is_palindrome_with_spaces(mod):
    """'taco cat' is a palindrome when spaces are ignored."""
    assert mod.is_palindrome("taco cat") is True


def test_is_palindrome_not_palindrome(mod):
    """'hello' is not a palindrome."""
    assert mod.is_palindrome("hello") is False


def test_is_palindrome_single_char(mod):
    """A single character is always a palindrome."""
    assert mod.is_palindrome("a") is True


# ---------------------------------------------------------------------------
# Tests — calculate_bmi
# ---------------------------------------------------------------------------

def test_calculate_bmi_normal(mod):
    """70kg at 1.75m should give a BMI of 22.9."""
    assert mod.calculate_bmi(70, 1.75) == 22.9


def test_calculate_bmi_overweight(mod):
    """90kg at 1.70m should give a BMI of 31.1."""
    assert mod.calculate_bmi(90, 1.70) == 31.1


def test_calculate_bmi_underweight(mod):
    """50kg at 1.80m should give a BMI of 15.4."""
    assert mod.calculate_bmi(50, 1.80) == 15.4


def test_calculate_bmi_returns_float(mod):
    """BMI should always be a float."""
    result = mod.calculate_bmi(70, 1.75)
    assert isinstance(result, float)
