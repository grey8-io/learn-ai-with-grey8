"""Linter unit tests."""

from pathlib import Path

import pytest

from ace.curator.linter import lint_lesson


@pytest.fixture()
def valid_lesson(tmp_path: Path) -> Path:
    """Create a minimal valid lesson directory."""
    lesson = tmp_path / "lesson-01"
    lesson.mkdir()

    (lesson / "content.md").write_text("# Lesson 1\n\nSome content here.\n")

    ex = lesson / "exercise-01"
    ex.mkdir()
    (ex / "starter.py").write_text("# TODO: implement\n")
    (ex / "solution.py").write_text("print('hello')\n")
    (ex / "tests.py").write_text("def test_hello(): pass\n")
    (ex / "hints.md").write_text("1. Think about it.\n")
    (ex / "rubric.md").write_text("| Criterion | Points |\n|---|---|\n| Works | 10 |\n")

    return lesson


@pytest.fixture()
def incomplete_lesson(tmp_path: Path) -> Path:
    """Create a lesson directory missing content.md."""
    lesson = tmp_path / "lesson-02"
    lesson.mkdir()
    return lesson


def test_valid_lesson_passes(valid_lesson: Path) -> None:
    issues = lint_lesson(valid_lesson)
    errors = [i for i in issues if i.severity == "error"]
    assert len(errors) == 0


def test_missing_content_md_caught(incomplete_lesson: Path) -> None:
    issues = lint_lesson(incomplete_lesson)
    error_messages = [i.message for i in issues if i.severity == "error"]
    assert any("content.md" in m for m in error_messages)


def test_missing_exercise_flagged(incomplete_lesson: Path) -> None:
    issues = lint_lesson(incomplete_lesson)
    warnings = [i for i in issues if i.severity == "warning"]
    assert any("exercise" in i.message.lower() for i in warnings)
