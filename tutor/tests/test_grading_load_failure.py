"""A file that fails to import must score 0, not get partial rubric credit."""

import textwrap
from pathlib import Path

import pytest

from tutor.grading.runner import run_tests

# A tiny test suite the runner can execute against the student's solution.py.
_TEST_SUITE = textwrap.dedent(
    """
    from solution import add


    def test_add_two_numbers():
        assert add(2, 3) == 5


    def test_add_negatives():
        assert add(-1, -1) == -2
    """
)


def _make_test_dir(tmp_path: Path) -> Path:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_exercise.py").write_text(_TEST_SUITE, encoding="utf-8")
    return tests_dir


@pytest.mark.asyncio
async def test_indentation_error_flags_load_failure(tmp_path):
    """A file Python can't import sets load_failed and yields no passing tests."""
    bad_code = textwrap.dedent(
        """
        def add(a, b):
        return a + b
        """
    )
    result = await run_tests(bad_code, _make_test_dir(tmp_path))

    assert result.load_failed is True
    assert result.passed is False
    assert result.passed_count == 0
    assert result.score == 0


@pytest.mark.asyncio
async def test_passing_code_does_not_flag_load_failure(tmp_path):
    """A clean file that passes its tests is never flagged as a load failure."""
    good_code = "def add(a, b):\n    return a + b\n"
    result = await run_tests(good_code, _make_test_dir(tmp_path))

    assert result.load_failed is False
    assert result.passed is True
    assert result.passed_count == result.total == 2


@pytest.mark.asyncio
async def test_logic_failure_is_not_a_load_failure(tmp_path):
    """A file that imports fine but fails a test is graded normally, not flagged."""
    wrong_code = "def add(a, b):\n    return a - b\n"
    result = await run_tests(wrong_code, _make_test_dir(tmp_path))

    assert result.load_failed is False
    assert result.passed is False
    # The file imported, so tests actually ran and produced pass/fail counts.
    assert result.total == 2
