"""Schema linter — checks lesson structure and file validity."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ace.shared.schema import validate_lesson


@dataclass
class LintIssue:
    """A single linting issue."""

    severity: str  # "error", "warning", "info"
    location: str
    message: str


def _check_structure(lesson_dir: Path) -> list[LintIssue]:
    """Check that the lesson directory has the expected file structure."""
    issues: list[LintIssue] = []

    expected_files = ["content.md"]
    for fname in expected_files:
        fpath = lesson_dir / fname
        if not fpath.exists():
            issues.append(
                LintIssue(
                    severity="error",
                    location=str(fpath),
                    message=f"Required file missing: {fname}",
                )
            )

    # Check for at least one exercise directory
    exercises = list(lesson_dir.glob("exercise-*"))
    if not exercises:
        issues.append(
            LintIssue(
                severity="warning",
                location=str(lesson_dir),
                message="No exercise directories found in lesson.",
            )
        )

    return issues


def _check_json_files(lesson_dir: Path) -> list[LintIssue]:
    """Validate any JSON files in the lesson directory."""
    issues: list[LintIssue] = []

    for json_file in lesson_dir.rglob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(
                LintIssue(
                    severity="error",
                    location=str(json_file),
                    message=f"Invalid JSON: {exc}",
                )
            )
            continue

        # If it looks like lesson metadata, validate against schema
        if json_file.name in ("meta.json", "lesson.json"):
            errors = validate_lesson(data)
            for err in errors:
                issues.append(
                    LintIssue(
                        severity="error",
                        location=str(json_file),
                        message=err,
                    )
                )

    return issues


def _check_markdown(lesson_dir: Path) -> list[LintIssue]:
    """Basic markdown formatting checks."""
    issues: list[LintIssue] = []

    for md_file in lesson_dir.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")

        # Check for empty files
        if not text.strip():
            issues.append(
                LintIssue(
                    severity="warning",
                    location=str(md_file),
                    message="Markdown file is empty.",
                )
            )
            continue

        # Check for a top-level heading in content.md
        if md_file.name == "content.md":
            lines = text.splitlines()
            has_heading = any(line.startswith("# ") for line in lines[:10])
            if not has_heading:
                issues.append(
                    LintIssue(
                        severity="info",
                        location=str(md_file),
                        message="content.md has no top-level heading in the first 10 lines.",
                    )
                )

        # Check for trailing whitespace (common formatting issue)
        for i, line in enumerate(text.splitlines(), start=1):
            if line != line.rstrip() and line.strip():
                issues.append(
                    LintIssue(
                        severity="info",
                        location=f"{md_file}:{i}",
                        message="Trailing whitespace.",
                    )
                )
                break  # Report only first occurrence per file

    return issues


def lint_lesson(lesson_path: Path) -> list[LintIssue]:
    """Run all lint checks on a lesson directory.

    Parameters
    ----------
    lesson_path:
        Path to the lesson directory.

    Returns
    -------
    list[LintIssue]
        All issues found, sorted by severity (errors first).
    """
    issues: list[LintIssue] = []
    issues.extend(_check_structure(lesson_path))
    issues.extend(_check_json_files(lesson_path))
    issues.extend(_check_markdown(lesson_path))

    severity_order = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda i: severity_order.get(i.severity, 9))
    return issues
