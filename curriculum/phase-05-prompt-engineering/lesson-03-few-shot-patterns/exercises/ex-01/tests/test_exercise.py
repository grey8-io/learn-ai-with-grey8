"""Tests for Exercise 1 — Advanced Prompt Patterns."""

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
# Tests — build_chain_of_thought_prompt
# ---------------------------------------------------------------------------

def test_cot_contains_question(mod):
    """CoT prompt should contain the question."""
    result = mod.build_chain_of_thought_prompt("What is 2+2?")
    assert "What is 2+2?" in result


def test_cot_contains_step_by_step(mod):
    """CoT prompt should include the step-by-step instruction."""
    result = mod.build_chain_of_thought_prompt("Why is the sky blue?")
    assert "step by step" in result.lower()


def test_cot_without_hint(mod):
    """CoT without hint should not contain extra instructions."""
    result = mod.build_chain_of_thought_prompt("Test question")
    assert result.endswith("Let's think step by step.")


def test_cot_with_hint(mod):
    """CoT with hint should append the hint."""
    result = mod.build_chain_of_thought_prompt("What is 10+5?", steps_hint="Add the numbers.")
    assert "Add the numbers." in result
    assert "step by step" in result.lower()


# ---------------------------------------------------------------------------
# Tests — build_few_shot_prompt
# ---------------------------------------------------------------------------

def test_few_shot_contains_task(mod):
    """Few-shot prompt should start with the task."""
    result = mod.build_few_shot_prompt("Classify", [], "test")
    assert result.startswith("Task: Classify")


def test_few_shot_formats_examples(mod):
    """Few-shot prompt should format all examples."""
    examples = [
        {"input": "hello", "output": "greeting"},
        {"input": "bye", "output": "farewell"},
    ]
    result = mod.build_few_shot_prompt("Classify", examples, "thanks")
    assert "Input: hello" in result
    assert "Output: greeting" in result
    assert "Input: bye" in result
    assert "Output: farewell" in result


def test_few_shot_ends_with_query(mod):
    """Few-shot prompt should end with the query and Output: marker."""
    result = mod.build_few_shot_prompt("Task", [], "my query")
    assert "Input: my query" in result
    assert result.rstrip().endswith("Output:")


def test_few_shot_no_examples(mod):
    """Few-shot prompt with no examples should still work."""
    result = mod.build_few_shot_prompt("Task", [], "query")
    assert "Task: Task" in result
    assert "Input: query" in result


# ---------------------------------------------------------------------------
# Tests — extract_final_answer
# ---------------------------------------------------------------------------

def test_extract_therefore(mod):
    """Should extract answer after 'Therefore'."""
    response = "Step 1: ...\nStep 2: ...\nTherefore, the answer is 42."
    result = mod.extract_final_answer(response)
    assert "42" in result


def test_extract_final_answer_marker(mod):
    """Should extract answer after 'Final answer:'."""
    response = "Some reasoning.\nFinal answer: Paris"
    result = mod.extract_final_answer(response)
    assert "Paris" in result


def test_extract_the_answer_is(mod):
    """Should extract answer after 'The answer is'."""
    response = "Let me think...\nThe answer is 100."
    result = mod.extract_final_answer(response)
    assert "100" in result


def test_extract_fallback_last_line(mod):
    """Should fall back to last non-empty line when no marker found."""
    response = "Step 1\nStep 2\n42"
    result = mod.extract_final_answer(response)
    assert "42" in result


def test_extract_strips_trailing_period(mod):
    """Should strip trailing period from answer."""
    response = "Therefore, the answer is 68."
    result = mod.extract_final_answer(response)
    assert not result.endswith(".")


# ---------------------------------------------------------------------------
# Tests — build_self_consistency_prompts
# ---------------------------------------------------------------------------

def test_self_consistency_returns_list(mod):
    """Should return a list of prompts."""
    result = mod.build_self_consistency_prompts("What is 5+5?")
    assert isinstance(result, list)


def test_self_consistency_correct_count(mod):
    """Should return exactly n prompts."""
    result = mod.build_self_consistency_prompts("What is 5+5?", n=5)
    assert len(result) == 5


def test_self_consistency_contains_question(mod):
    """All prompts should contain the original question."""
    result = mod.build_self_consistency_prompts("What is 5+5?", n=3)
    for prompt in result:
        assert "What is 5+5?" in prompt


def test_self_consistency_different_prompts(mod):
    """Prompts should differ from each other (different prefixes)."""
    result = mod.build_self_consistency_prompts("Question?", n=3)
    assert len(set(result)) == 3  # all unique


def test_self_consistency_wraps_around(mod):
    """Should cycle through prefixes when n exceeds prefix count."""
    result = mod.build_self_consistency_prompts("Q?", n=7)
    assert len(result) == 7
    # First and sixth should be the same prefix (cycling with 5 prefixes)
    assert result[0] == result[5]
