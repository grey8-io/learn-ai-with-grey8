"""Tiered context builder for the tutor LLM.

Assembles context layers based on the runtime model's context window size:

  ALWAYS (any model):
    - System prompt (~200 tokens)
    - Student profile (~100 tokens)
    - Phase roadmap (~30 tokens)
    - Current lesson content (~800 tokens)

  MEDIUM+ (8K+ context):
    - Curriculum index — all lesson summaries (~500 tokens)

  Exercise mode (any model):
    - Starter TODO comments
    - Test function names
    - Submission history summary

  Chat history fills remaining budget.
"""

import json
from pathlib import Path

from tutor.config import settings

# Compute curriculum path directly from this file's location — CWD-independent.
# __file__ is tutor/tutor/engine/context.py → project root is 4 levels up.
from pathlib import Path as _Path
_CURRICULUM_DIR = _Path(__file__).resolve().parent.parent.parent.parent / "curriculum"
from tutor.engine.prompts import TUTOR_SYSTEM_PROMPT
from tutor.engine.student_profile import profile_to_text
from tutor.models.schemas import StudentProfile


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token."""
    return len(text) // 4


# ---- Loaders ----------------------------------------------------------------

def load_lesson_content(lesson_id: str) -> str:
    """Load the content.md file for a given lesson_id."""
    content_path = _CURRICULUM_DIR / lesson_id / "content.md"
    if content_path.exists():
        return content_path.read_text(encoding="utf-8")
    return ""


def load_exercise_metadata(exercise_id: str) -> dict:
    """Load exercise metadata (rubric, hints) for a given exercise."""
    # Resolve URL-encoded ID to filesystem path
    base = resolve_exercise_path(exercise_id)
    if not base:
        base = _CURRICULUM_DIR / exercise_id

    meta: dict = {}

    hints_path = base / "hints.json"
    if hints_path.exists():
        meta["hints"] = json.loads(hints_path.read_text(encoding="utf-8"))

    rubric_path = base / "rubric.md"
    if rubric_path.exists():
        meta["rubric"] = rubric_path.read_text(encoding="utf-8")

    return meta


def resolve_exercise_path(exercise_id: str) -> Path | None:
    """Resolve a URL-encoded exercise ID to its filesystem path.

    Exercise IDs come as "phase-01--lesson-02--ex-01" from the frontend.
    The manifest has the actual directory paths like
    "phase-01-dev-environment/lesson-02-python-setup/exercises/ex-01".

    Returns the absolute exercise directory path, or None if not found.
    """
    # Split URL-encoded ID: "phase-01--lesson-02--ex-01" -> ["phase-01", "lesson-02", "ex-01"]
    parts = exercise_id.split("--")
    if len(parts) < 3:
        return None

    exercise_local_id = parts[-1]  # "ex-01"
    lesson_id = "/".join(parts[:-1])  # "phase-01/lesson-02"

    manifest_path = _CURRICULUM_DIR / "manifest.json"
    if not manifest_path.exists():
        return None

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    for phase in manifest.get("phases", []):
        for lesson in phase.get("lessons", []):
            if lesson["id"] == lesson_id:
                for ex in lesson.get("exercises", []):
                    if ex["id"] == exercise_local_id:
                        # Derive exercise dir from test_file path
                        test_file = ex.get("test_file", "")
                        if test_file:
                            # test_file: "phase-01-dev-.../exercises/ex-01/tests/test_exercise.py"
                            # exercise dir: everything up to /tests/
                            ex_dir = str(Path(test_file).parent.parent)
                            return _CURRICULUM_DIR / ex_dir
                        # Fallback: derive from starter_file
                        starter = ex.get("starter_file", "")
                        if starter:
                            ex_dir = str(Path(starter).parent.parent)
                            return _CURRICULUM_DIR / ex_dir
    return None


def get_tests_dir(exercise_id: str) -> Path | None:
    """Return the tests directory for an exercise, or None."""
    # Try resolving URL-encoded ID first
    ex_path = resolve_exercise_path(exercise_id)
    if ex_path:
        tests_dir = ex_path / "tests"
        if tests_dir.is_dir():
            return tests_dir

    # Fallback: try direct path (for canonical IDs)
    tests_dir = _CURRICULUM_DIR / exercise_id / "tests"
    if tests_dir.is_dir():
        return tests_dir
    return None


def _load_curriculum_index() -> str:
    """Load the pre-generated curriculum index as a compact text block."""
    index_path = _CURRICULUM_DIR / "curriculum_index.json"
    if not index_path.exists():
        return ""

    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""

    lines = ["=== Curriculum Index (all lessons) ==="]
    for lesson in data.get("lessons", []):
        phase = lesson.get("phase", "?")
        title = lesson.get("title", "")
        summary = lesson.get("summary", "")
        concepts = ", ".join(lesson.get("concepts", [])[:4])
        lines.append(f"Phase {phase}: {title} — {summary} [Topics: {concepts}]")

    return "\n".join(lines)


def _build_roadmap(lesson_id: str, manifest_path: Path | None = None) -> str:
    """Build a phase roadmap showing where the student is in the journey."""
    mpath = manifest_path or (_CURRICULUM_DIR / "manifest.json")
    if not mpath.exists():
        return ""

    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""

    # Find current lesson position
    all_lessons = []
    current_phase_num = 0
    current_lesson_idx = 0
    phase_title = ""

    for phase in manifest.get("phases", []):
        for i, lesson in enumerate(phase.get("lessons", [])):
            all_lessons.append(lesson)
            if lesson["id"] == lesson_id:
                current_phase_num = phase["phase"]
                current_lesson_idx = i + 1
                phase_title = phase["title"]

    if not current_phase_num:
        return ""

    total_in_phase = sum(
        len(p["lessons"]) for p in manifest["phases"]
        if p["phase"] == current_phase_num
    )

    return (
        f"=== Roadmap ===\n"
        f"Currently on: Phase {current_phase_num} ({phase_title}), "
        f"Lesson {current_lesson_idx} of {total_in_phase}. "
        f"Total progress: {len(all_lessons)} lessons across 12 phases."
    )


def _load_exercise_context(lesson_id: str) -> str:
    """Load exercise-specific context: TODO comments from starter and test names."""
    base = _CURRICULUM_DIR / lesson_id / "exercises" / "ex-01"

    parts = []

    # Extract TODO comments from starter
    starter = base / "starter" / "main.py"
    if starter.exists():
        todos = []
        for line in starter.read_text(encoding="utf-8").split("\n"):
            stripped = line.strip()
            if stripped.startswith("# TODO"):
                todos.append(stripped)
        if todos:
            parts.append("Exercise TODOs:\n" + "\n".join(todos))

    # Extract test function names (without revealing implementation)
    tests_dir = base / "tests"
    if tests_dir.is_dir():
        test_names = []
        for tf in tests_dir.glob("test_*.py"):
            import re
            for match in re.finditer(
                r"^def (test_\w+)", tf.read_text(encoding="utf-8"), re.MULTILINE
            ):
                test_names.append(match.group(1))
        if test_names:
            parts.append("Tests the student must pass: " + ", ".join(test_names))

    return "\n".join(parts) if parts else ""


# ---- Main builder -----------------------------------------------------------

# Context budget tiers based on model context window
TIER_SMALL = 2048     # 1B-3B models
TIER_MEDIUM = 8192    # 7B-8B models
TIER_LARGE = 16384    # 13B+ models


async def build_context(
    lesson_id: str,
    student_code: str = "",
    history: list[dict[str, str]] | None = None,
    student_profile: StudentProfile | None = None,
    model_context_length: int = 2048,
) -> tuple[str, list[dict[str, str]]]:
    """Assemble tiered context based on model's context window.

    Returns (system_prompt_with_context, trimmed_history).
    """
    # Determine tier
    is_medium = model_context_length >= TIER_MEDIUM
    is_large = model_context_length >= TIER_LARGE

    # Reserve tokens for response generation
    response_reserve = min(1024, model_context_length // 4)
    total_budget = model_context_length - response_reserve

    # ---- Layer 1: System prompt (always) ----
    system = TUTOR_SYSTEM_PROMPT

    # ---- Layer 2: Student profile (always, ~100 tokens) ----
    profile_text = profile_to_text(student_profile)
    if profile_text:
        system += "\n\n" + profile_text

    # ---- Layer 3: Roadmap (always, ~30 tokens) ----
    roadmap = _build_roadmap(lesson_id)
    if roadmap:
        system += "\n\n" + roadmap

    # ---- Layer 4: Current lesson content (always) ----
    lesson_content = load_lesson_content(lesson_id)

    # ---- Layer 5: Exercise context (if applicable) ----
    exercise_context = ""
    if student_code:
        exercise_context = _load_exercise_context(lesson_id)

    # ---- Layer 6: Curriculum index (medium+ models) ----
    curriculum_index = ""
    if is_medium:
        curriculum_index = _load_curriculum_index()

    # Build the context block
    context_parts = ["=== Current Lesson ===", lesson_content]

    if exercise_context:
        context_parts.append("\n=== Exercise Context ===")
        context_parts.append(exercise_context)
        if student_code:
            context_parts.append(f"\n=== Student's Code ===\n```python\n{student_code}\n```")

    if curriculum_index:
        context_parts.append("\n" + curriculum_index)

    context = "\n".join(context_parts)

    # Truncate lesson content if it exceeds budget
    context_tokens = _estimate_tokens(system + context)
    if context_tokens > total_budget * 0.7:  # leave 30% for history
        max_lesson_chars = int(total_budget * 0.5) * 4
        if len(lesson_content) > max_lesson_chars:
            lesson_content = lesson_content[:max_lesson_chars] + "\n... (truncated)"
            # Rebuild context with truncated content
            context_parts[1] = lesson_content
            context = "\n".join(context_parts)

    full_system = system + "\n\n" + context

    # ---- Trim chat history to fit remaining budget ----
    system_tokens = _estimate_tokens(full_system)
    history_budget = total_budget - system_tokens

    trimmed: list[dict[str, str]] = []
    if history:
        # Keep most recent messages, trim from the front
        total_history_tokens = 0
        for msg in reversed(history):
            msg_tokens = _estimate_tokens(msg.get("content", ""))
            if total_history_tokens + msg_tokens > history_budget:
                break
            trimmed.insert(0, msg)
            total_history_tokens += msg_tokens

    return full_system, trimmed
