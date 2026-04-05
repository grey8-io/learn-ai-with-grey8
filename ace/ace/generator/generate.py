"""Content generator — turns YAML specs into curriculum files."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import yaml

from ace.shared.config import get_settings
from ace.shared.ollama import generate as llm_generate

logger = logging.getLogger(__name__)


def _load_template(name: str) -> str:
    """Load a prompt template from the templates directory."""
    template_path = Path(__file__).parent / "templates" / name
    return template_path.read_text(encoding="utf-8")


def _write(path: Path, content: str) -> None:
    """Write content to a file, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _generate_lesson_content(lesson: dict[str, Any]) -> str:
    """Generate lesson markdown via LLM."""
    template = _load_template("lesson_prompt.txt")
    prompt = template.format(
        title=lesson["title"],
        objectives="\n".join(f"- {o}" for o in lesson.get("objectives", [])),
        target_audience=lesson.get("target_audience", "beginners"),
        prerequisites=", ".join(lesson.get("prerequisites", [])),
    )
    return llm_generate(
        prompt=prompt,
        system="You are an expert programming instructor. Write clear, concise lesson content in Markdown.",
    )


def _generate_exercise(exercise: dict[str, Any], lesson_title: str) -> dict[str, str]:
    """Generate exercise files (starter, solution, tests, hints, rubric) via LLM."""
    template = _load_template("exercise_prompt.txt")
    prompt = template.format(
        lesson_title=lesson_title,
        exercise_title=exercise.get("title", "Exercise"),
        description=exercise.get("description", ""),
        difficulty=exercise.get("difficulty", "beginner"),
        objectives="\n".join(f"- {o}" for o in exercise.get("objectives", [])),
        exercise_type=exercise.get("type", "coding"),
    )
    raw = llm_generate(
        prompt=prompt,
        system=(
            "You are an expert programming instructor. Generate exercise files. "
            "Use the exact section headers: ## STARTER, ## SOLUTION, ## TESTS, "
            "## HINTS, ## RUBRIC. Separate each section clearly. "
            "For the HINTS section, output exactly 3 short hint strings, "
            "one per line (no bullet points or numbering)."
        ),
    )
    return _parse_exercise_sections(raw)


def _parse_exercise_sections(raw: str) -> dict[str, str]:
    """Split LLM output into exercise sections."""
    sections: dict[str, str] = {
        "starter": "",
        "solution": "",
        "tests": "",
        "hints": "",
        "rubric": "",
    }
    current: str | None = None
    lines: list[str] = []

    for line in raw.splitlines():
        header = line.strip().lower().lstrip("#").strip()
        if header in sections:
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = header
            lines = []
        else:
            lines.append(line)

    if current is not None:
        sections[current] = "\n".join(lines).strip()

    return sections


def _hints_to_json(hints_text: str) -> str:
    """Convert raw hints text into a JSON array of 3 strings."""
    # Parse non-empty lines, stripping bullets/numbering
    hint_lines = []
    for line in hints_text.splitlines():
        cleaned = line.strip().lstrip("-*0123456789.)").strip()
        if cleaned:
            hint_lines.append(cleaned)

    # Pad or truncate to exactly 3 hints
    while len(hint_lines) < 3:
        hint_lines.append("Review the lesson content for more guidance.")
    hint_lines = hint_lines[:3]

    return json.dumps(hint_lines, indent=2)


def _generate_quiz(lesson: dict[str, Any]) -> str:
    """Generate quiz questions via LLM, returning JSON."""
    template = _load_template("quiz_prompt.txt")
    prompt = template.format(
        title=lesson["title"],
        objectives="\n".join(f"- {o}" for o in lesson.get("objectives", [])),
    )
    return llm_generate(
        prompt=prompt,
        system=(
            "You are an expert programming instructor. Generate quiz questions. "
            "Output ONLY valid JSON — no markdown fences, no commentary. "
            "The JSON must be an array of objects, each with: "
            '"question" (string), "options" (array of 4 strings), '
            '"correct" (integer 0-3 for the index of the right answer), '
            '"explanation" (string).'
        ),
    )


def _clean_json_response(raw: str) -> str:
    """Strip markdown fences and leading/trailing whitespace from LLM JSON."""
    text = raw.strip()
    # Remove ```json ... ``` wrapping if present
    if text.startswith("```"):
        # Remove first line (```json or ```)
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


def generate_from_spec(spec_path: Path) -> dict[str, int]:
    """Generate curriculum content from a YAML spec file.

    Parameters
    ----------
    spec_path:
        Path to the YAML specification file.

    Returns
    -------
    dict
        Summary counts: lessons, exercises, quizzes generated.
    """
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    settings = get_settings()
    base = settings.curriculum_path

    phase_id: str = spec.get("phase", "00")
    phase_slug: str = spec.get("phase_slug", "")
    if phase_slug:
        phase_dir = base / f"phase-{phase_id}-{phase_slug}"
    else:
        phase_dir = base / f"phase-{phase_id}"

    lessons_generated = 0
    exercises_generated = 0
    quizzes_generated = 0

    for lesson_spec in spec.get("lessons", []):
        # Build lesson directory name from slug or fallback to id
        lesson_id: str = lesson_spec.get("id", f"lesson-{lessons_generated + 1:02d}")
        lesson_slug: str = lesson_spec.get("slug", "")
        if lesson_slug:
            lesson_dir_name = f"{lesson_id}-{lesson_slug}"
        else:
            lesson_dir_name = lesson_id
        lesson_dir = phase_dir / lesson_dir_name

        # Generate lesson content
        content_md = _generate_lesson_content(lesson_spec)
        _write(lesson_dir / "content.md", content_md)
        lessons_generated += 1

        # Generate exercises
        for i, exercise_spec in enumerate(lesson_spec.get("exercises", []), start=1):
            ex_dir = lesson_dir / "exercises" / f"ex-{i:02d}"
            sections = _generate_exercise(exercise_spec, lesson_spec["title"])
            _write(ex_dir / "starter" / "main.py", sections["starter"])
            _write(ex_dir / "solution" / "main.py", sections["solution"])
            _write(ex_dir / "tests" / "test_exercise.py", sections["tests"])
            _write(ex_dir / "rubric.md", sections["rubric"])
            _write(ex_dir / "hints.json", _hints_to_json(sections["hints"]))
            exercises_generated += 1

        # Generate quiz as JSON
        quiz_raw = _generate_quiz(lesson_spec)
        quiz_json = _clean_json_response(quiz_raw)
        _write(lesson_dir / "quiz.json", quiz_json + "\n")
        quizzes_generated += 1

    # Auto-sync manifest and docs after generation
    try:
        from ace.sync import sync_all

        repo_root = base.parent  # curriculum/ -> repo root
        sync_report = sync_all(repo_root)
        if sync_report.manifest_updated:
            logger.info("Auto-sync: manifest.json updated with new lessons")
        if sync_report.readme_updated:
            logger.info("Auto-sync: README.md curriculum table updated")
        if sync_report.issues:
            for issue in sync_report.issues:
                logger.warning("Auto-sync issue: %s", issue)
    except Exception:
        logger.warning("Auto-sync after generation failed", exc_info=True)

    return {
        "lessons": lessons_generated,
        "exercises": exercises_generated,
        "quizzes": quizzes_generated,
    }
