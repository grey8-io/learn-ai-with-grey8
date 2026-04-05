"""Analytics reflector — generates curriculum reports."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ace.reflector.analytics import (
    compute_difficulty_distribution,
    detect_gaps,
    measure_coverage,
)
from ace.shared.config import get_settings


def _discover_phases(curriculum_path: Path) -> list[Path]:
    """Return sorted phase directories."""
    return sorted(
        p for p in curriculum_path.iterdir() if p.is_dir() and p.name.startswith("phase-")
    )


def _discover_lessons(phase_path: Path) -> list[Path]:
    """Return sorted lesson directories within a phase."""
    return sorted(
        p for p in phase_path.iterdir() if p.is_dir() and p.name.startswith("lesson-")
    )


def _count_exercises(lesson_path: Path) -> int:
    """Count exercise directories in a lesson."""
    exercises_dir = lesson_path / "exercises"
    if exercises_dir.exists():
        return len([p for p in exercises_dir.iterdir() if p.is_dir() and p.name.startswith("ex-")])
    return len([p for p in lesson_path.iterdir() if p.is_dir() and p.name.startswith("exercise-")])


def _parse_phase_num(phase_path: Path) -> int:
    """Extract numeric phase number from directory name like 'phase-01-foo'."""
    try:
        return int(phase_path.name.split("-")[1])
    except (IndexError, ValueError):
        return 0


def generate_report(output_path: Path) -> None:
    """Analyze the curriculum and write a Markdown report.

    Parameters
    ----------
    output_path:
        File path where the report will be written.
    """
    settings = get_settings()
    curriculum = settings.curriculum_path

    lines: list[str] = []
    lines.append("# ACE Curriculum Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")

    if not curriculum.exists():
        lines.append(f"> Curriculum path `{curriculum}` does not exist.")
        _write_report(output_path, lines)
        return

    phases = _discover_phases(curriculum)
    lines.append(f"## Overview")
    lines.append("")
    lines.append(f"- **Phases found:** {len(phases)}")

    total_lessons = 0
    total_exercises = 0

    lines.append("")
    lines.append("## Phase Breakdown")
    lines.append("")
    lines.append("| Phase | Lessons | Exercises |")
    lines.append("|-------|---------|-----------|")

    for phase in phases:
        lessons = _discover_lessons(phase)
        exercises = sum(_count_exercises(l) for l in lessons)
        total_lessons += len(lessons)
        total_exercises += exercises
        lines.append(f"| {phase.name} | {len(lessons)} | {exercises} |")

    lines.append("")
    lines.append(f"**Totals:** {total_lessons} lessons, {total_exercises} exercises")
    lines.append("")

    # Difficulty distribution
    lines.append("## Difficulty Distribution")
    lines.append("")
    distribution = compute_difficulty_distribution(curriculum)
    if distribution:
        lines.append("| Difficulty | Count |")
        lines.append("|------------|-------|")
        for diff, count in sorted(distribution.items()):
            lines.append(f"| {diff} | {count} |")
    else:
        lines.append("_No difficulty metadata found._")
    lines.append("")

    # Gap detection
    lines.append("## Gap Analysis")
    lines.append("")
    gaps = detect_gaps(curriculum)
    if gaps:
        for gap in gaps:
            lines.append(f"- {gap}")
    else:
        lines.append("_No gaps detected._")
    lines.append("")

    # Coverage
    lines.append("## Topic Coverage")
    lines.append("")
    coverage = measure_coverage(curriculum)
    if coverage:
        for topic, status in sorted(coverage.items()):
            marker = "x" if status else " "
            lines.append(f"- [{marker}] {topic}")
    else:
        lines.append("_No coverage data available._")
    lines.append("")

    # Content Health
    lines.append("## Content Health")
    lines.append("")
    lines.append("| Phase | Status | Lessons | Exercises | Has Quiz | Notes |")
    lines.append("|-------|--------|---------|-----------|----------|-------|")

    for phase in phases:
        lessons = _discover_lessons(phase)
        exercises = sum(_count_exercises(l) for l in lessons)
        has_all_content = all((l / "content.md").exists() for l in lessons)
        has_quizzes = all(
            (l / "quiz.json").exists() or (l / "quiz.md").exists()
            for l in lessons
        )
        status = "Complete" if (has_all_content and lessons) else "Stub"
        notes_parts: list[str] = []
        if not lessons:
            status = "Empty"
            notes_parts.append("no lessons yet")
        elif not has_all_content:
            notes_parts.append("missing content.md")
        if lessons and not has_quizzes:
            notes_parts.append("missing quizzes")
        notes = "; ".join(notes_parts) if notes_parts else "--"
        quiz_mark = "Yes" if has_quizzes and lessons else "No"
        lines.append(
            f"| {phase.name} | {status} | {len(lessons)} | {exercises} | {quiz_mark} | {notes} |"
        )

    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    if total_lessons == 0:
        lines.append("- Start by generating content for Phase 1 using `ace generate`.")
    else:
        # Exercise density
        avg_exercises = total_exercises / max(total_lessons, 1)
        if avg_exercises < 2:
            lines.append(
                f"- Average exercises per lesson is {avg_exercises:.1f} — consider adding more (aim for 2+)."
            )

        # Check for phases with few lessons
        for phase in phases:
            lessons = _discover_lessons(phase)
            ex_count = sum(_count_exercises(l) for l in lessons)
            if 0 < len(lessons) < 2:
                lines.append(
                    f"- **{phase.name}** has only {len(lessons)} lesson(s) — consider expanding."
                )
            if lessons and ex_count < len(lessons):
                lines.append(
                    f"- **{phase.name}** has {ex_count} exercise(s) for {len(lessons)} lessons — some lessons lack exercises."
                )

        # Difficulty progression check
        phase_names = [p.name for p in phases]
        if len(phase_names) > 2:
            # Check for big jumps by looking at phase numbers
            phase_nums = [_parse_phase_num(p) for p in phases]
            for i in range(len(phase_nums) - 1):
                if phase_nums[i + 1] - phase_nums[i] > 1:
                    lines.append(
                        f"- Gap between {phases[i].name} and {phases[i+1].name} — "
                        f"consider an intermediate phase or bridging lesson."
                    )

        if gaps:
            lines.append("- Address the gaps listed in **Gap Analysis** above to ensure smooth progression.")
        lines.append("- Run `ace curate` on each phase to check content quality.")
        lines.append("- Run `ace sync` to ensure manifest.json stays current with disk.")

    lines.append("")

    _write_report(output_path, lines)


def _write_report(output_path: Path, lines: list[str]) -> None:
    """Write lines to the output file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
