"""Analytics helpers for the ACE reflector."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def compute_difficulty_distribution(curriculum_path: Path) -> dict[str, int]:
    """Count exercises by difficulty across the entire curriculum.

    Looks for ``meta.json`` files inside exercise directories that contain
    a ``"difficulty"`` field.

    Returns
    -------
    dict
        Mapping of difficulty label to count.
    """
    distribution: dict[str, int] = {}

    for meta_file in curriculum_path.rglob("exercise-*/meta.json"):
        try:
            data: dict[str, Any] = json.loads(meta_file.read_text(encoding="utf-8"))
            diff = data.get("difficulty", "unknown")
            distribution[diff] = distribution.get(diff, 0) + 1
        except (json.JSONDecodeError, OSError):
            continue

    return distribution


def detect_gaps(curriculum_path: Path) -> list[str]:
    """Detect potential curriculum gaps.

    Checks for:
    - Non-sequential phase numbering
    - Non-sequential lesson numbering within phases
    - Phases with zero lessons

    Returns
    -------
    list[str]
        Human-readable descriptions of detected gaps.
    """
    gaps: list[str] = []

    phases = sorted(
        p for p in curriculum_path.iterdir() if p.is_dir() and p.name.startswith("phase-")
    ) if curriculum_path.exists() else []

    # Check phase numbering
    phase_numbers: list[int] = []
    for phase in phases:
        try:
            num = int(phase.name.split("-")[1])
            phase_numbers.append(num)
        except (IndexError, ValueError):
            gaps.append(f"Phase directory with unexpected name: {phase.name}")

    for i in range(len(phase_numbers) - 1):
        if phase_numbers[i + 1] - phase_numbers[i] > 1:
            gaps.append(
                f"Gap between phase-{phase_numbers[i]:02d} and phase-{phase_numbers[i+1]:02d}"
            )

    # Check lessons within each phase
    for phase in phases:
        lessons = sorted(
            p for p in phase.iterdir() if p.is_dir() and p.name.startswith("lesson-")
        )
        if not lessons:
            gaps.append(f"{phase.name} has no lessons.")
            continue

        lesson_numbers: list[int] = []
        for lesson in lessons:
            try:
                num = int(lesson.name.split("-")[1])
                lesson_numbers.append(num)
            except (IndexError, ValueError):
                gaps.append(f"Lesson directory with unexpected name: {lesson.name} in {phase.name}")

        for i in range(len(lesson_numbers) - 1):
            if lesson_numbers[i + 1] - lesson_numbers[i] > 1:
                gaps.append(
                    f"Gap in {phase.name}: lesson-{lesson_numbers[i]:02d} "
                    f"to lesson-{lesson_numbers[i+1]:02d}"
                )

    return gaps


def measure_coverage(curriculum_path: Path) -> dict[str, bool]:
    """Check topic coverage against a target skill list.

    Reads ``curriculum_path/topics.json`` if it exists. The file should
    contain a JSON object mapping topic names to ``true`` (covered) or
    ``false`` (not yet covered). If the file does not exist, returns an
    empty dict.

    Returns
    -------
    dict
        Topic name to coverage boolean.
    """
    topics_file = curriculum_path / "topics.json"
    if not topics_file.exists():
        return {}

    try:
        data = json.loads(topics_file.read_text(encoding="utf-8"))
        return {str(k): bool(v) for k, v in data.items()}
    except (json.JSONDecodeError, OSError):
        return {}
