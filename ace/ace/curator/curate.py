"""Content curator — runs quality checks on curriculum content."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ace.curator.linter import LintIssue, lint_lesson
from ace.shared.ollama import OllamaError, generate as llm_generate


@dataclass
class CurationReport:
    """Result of curating a curriculum path."""

    issues: list[LintIssue] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    score: int = 100


def _check_exercise_completeness(lesson_dir: Path) -> list[LintIssue]:
    """Check that each exercise directory has all required files."""
    issues: list[LintIssue] = []
    required_files = ["starter.py", "solution.py", "tests.py", "hints.md", "rubric.md"]

    for ex_dir in sorted(lesson_dir.glob("exercise-*")):
        if not ex_dir.is_dir():
            continue
        for fname in required_files:
            if not (ex_dir / fname).exists():
                issues.append(
                    LintIssue(
                        severity="error",
                        location=str(ex_dir / fname),
                        message=f"Missing required exercise file: {fname}",
                    )
                )
    return issues


def _check_readability(content_path: Path) -> list[LintIssue]:
    """Basic readability checks on markdown content."""
    issues: list[LintIssue] = []
    if not content_path.exists():
        return issues

    text = content_path.read_text(encoding="utf-8")
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]

    long_sentences = [s for s in sentences if len(s.split()) > 40]
    if long_sentences:
        issues.append(
            LintIssue(
                severity="warning",
                location=str(content_path),
                message=f"{len(long_sentences)} sentence(s) exceed 40 words — consider simplifying.",
            )
        )

    if len(text) < 200:
        issues.append(
            LintIssue(
                severity="warning",
                location=str(content_path),
                message="Content seems very short (< 200 chars). Consider expanding.",
            )
        )

    return issues


def _check_content_quality_via_llm(content_path: Path) -> list[str]:
    """Use the LLM to review content quality. Returns suggestions."""
    if not content_path.exists():
        return []

    text = content_path.read_text(encoding="utf-8")
    if len(text) < 50:
        return ["Content is too short for meaningful LLM review."]

    # Truncate to avoid huge prompts
    truncated = text[:3000]

    try:
        response = llm_generate(
            prompt=(
                f"Review this lesson content for clarity, accuracy, and appropriate "
                f"difficulty for beginners. List up to 5 specific, actionable suggestions "
                f"for improvement. Be concise.\n\n---\n{truncated}\n---"
            ),
            system="You are a curriculum quality reviewer. Be constructive and specific.",
        )
        return [line.strip() for line in response.strip().splitlines() if line.strip()]
    except OllamaError:
        return ["LLM review skipped — Ollama not available."]


def _check_deduplication(lesson_dir: Path, curriculum_root: Path) -> list[LintIssue]:
    """Simple overlap detection against other lessons."""
    issues: list[LintIssue] = []
    content_path = lesson_dir / "content.md"
    if not content_path.exists():
        return issues

    current_text = content_path.read_text(encoding="utf-8").lower()
    current_words = set(current_text.split())

    for other_content in curriculum_root.rglob("content.md"):
        if other_content.resolve() == content_path.resolve():
            continue
        other_text = other_content.read_text(encoding="utf-8").lower()
        other_words = set(other_text.split())

        if not current_words or not other_words:
            continue

        overlap = len(current_words & other_words) / min(len(current_words), len(other_words))
        if overlap > 0.7:
            issues.append(
                LintIssue(
                    severity="warning",
                    location=str(content_path),
                    message=f"High content overlap ({overlap:.0%}) with {other_content}",
                )
            )

    return issues


def curate_path(path: Path) -> CurationReport:
    """Run all quality checks on the curriculum at *path*.

    Parameters
    ----------
    path:
        Root directory of the curriculum content to check (e.g. a phase or
        lesson directory).

    Returns
    -------
    CurationReport
        Structured report with issues, suggestions, and an overall score.
    """
    report = CurationReport()

    # Find the curriculum root (walk up until we find a phase-* directory or use path)
    curriculum_root = path

    # Collect all lesson directories
    lesson_dirs = sorted(path.rglob("lesson-*"))
    if not lesson_dirs:
        # Maybe path itself is a lesson directory
        if (path / "content.md").exists():
            lesson_dirs = [path]

    if not lesson_dirs:
        report.issues.append(
            LintIssue(
                severity="warning",
                location=str(path),
                message="No lesson directories found.",
            )
        )
        report.score = 0
        return report

    for lesson_dir in lesson_dirs:
        if not lesson_dir.is_dir():
            continue

        # Schema / structure linting
        report.issues.extend(lint_lesson(lesson_dir))

        # Exercise completeness
        report.issues.extend(_check_exercise_completeness(lesson_dir))

        # Readability
        report.issues.extend(_check_readability(lesson_dir / "content.md"))

        # Deduplication
        report.issues.extend(_check_deduplication(lesson_dir, curriculum_root))

        # LLM quality review
        suggestions = _check_content_quality_via_llm(lesson_dir / "content.md")
        report.suggestions.extend(suggestions)

    # Compute score: start at 100, deduct per issue
    deductions = {"error": 15, "warning": 5, "info": 1}
    for issue in report.issues:
        report.score -= deductions.get(issue.severity, 0)
    report.score = max(0, report.score)

    return report
