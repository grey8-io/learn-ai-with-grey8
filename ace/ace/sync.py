"""Auto-sync module — keeps manifest, README, and docs in sync with curriculum on disk."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SyncReport:
    """Result of a sync operation."""

    files_added: list[str] = field(default_factory=list)
    files_removed: list[str] = field(default_factory=list)
    manifest_updated: bool = False
    readme_updated: bool = False
    getting_started_updated: bool = False
    issues: list[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        """Return True if anything was out of sync."""
        return bool(
            self.files_added
            or self.files_removed
            or self.manifest_updated
            or self.readme_updated
            or self.getting_started_updated
            or self.issues
        )

    def summary(self) -> str:
        """Return a human-readable summary."""
        lines: list[str] = []
        if self.files_added:
            lines.append(f"Lessons added to manifest: {len(self.files_added)}")
            for f in self.files_added:
                lines.append(f"  + {f}")
        if self.files_removed:
            lines.append(f"Lessons removed from manifest: {len(self.files_removed)}")
            for f in self.files_removed:
                lines.append(f"  - {f}")
        if self.manifest_updated:
            lines.append("manifest.json updated")
        if self.readme_updated:
            lines.append("README.md curriculum table updated")
        if self.getting_started_updated:
            lines.append("docs/GETTING_STARTED.md updated")
        if self.issues:
            lines.append(f"Issues found: {len(self.issues)}")
            for issue in self.issues:
                lines.append(f"  ! {issue}")
        if not lines:
            lines.append("Everything is in sync.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Filesystem scanning
# ---------------------------------------------------------------------------

def _discover_phases(curriculum_path: Path) -> list[Path]:
    """Return sorted phase directories."""
    return sorted(
        p for p in curriculum_path.iterdir()
        if p.is_dir() and re.match(r"phase-\d{2}", p.name)
    )


def _discover_lessons(phase_path: Path) -> list[Path]:
    """Return sorted lesson directories within a phase."""
    return sorted(
        p for p in phase_path.iterdir()
        if p.is_dir() and re.match(r"lesson-\d{2}", p.name)
    )


def _extract_title_from_content(content_md: Path) -> str:
    """Extract the first H1 heading from a content.md file."""
    if not content_md.exists():
        return "Untitled"
    for line in content_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    return "Untitled"


def _count_exercises(lesson_path: Path) -> list[Path]:
    """Return sorted exercise directories in a lesson."""
    exercises_dir = lesson_path / "exercises"
    if not exercises_dir.exists():
        return []
    return sorted(
        p for p in exercises_dir.iterdir()
        if p.is_dir() and re.match(r"ex-\d{2}", p.name)
    )


def _parse_phase_number(phase_dir: Path) -> int:
    """Extract the numeric phase ID from a directory name like 'phase-01-foo'."""
    return int(phase_dir.name.split("-")[1])


def _parse_lesson_number(lesson_dir: Path) -> int:
    """Extract the numeric lesson ID from a directory name like 'lesson-02-bar'."""
    return int(lesson_dir.name.split("-")[1])


def _build_lesson_entry(
    phase_dir: Path,
    lesson_dir: Path,
    phase_num: int,
    lesson_num: int,
) -> dict[str, Any]:
    """Build a manifest lesson entry from a lesson directory on disk."""
    content_path = lesson_dir / "content.md"
    title = _extract_title_from_content(content_path)

    # Build relative content_file path (relative to curriculum/)
    content_file = f"{phase_dir.name}/{lesson_dir.name}/content.md"

    # Quiz
    quiz_file: str | None = None
    quiz_path = lesson_dir / "quiz.json"
    if quiz_path.exists():
        quiz_file = f"{phase_dir.name}/{lesson_dir.name}/quiz.json"

    # Exercises
    exercises: list[dict[str, Any]] = []
    for ex_dir in _count_exercises(lesson_dir):
        ex_entry: dict[str, Any] = {
            "id": ex_dir.name,
            "title": ex_dir.name.replace("-", " ").title(),
            "difficulty": "medium",
        }
        # Look for known files
        for key, pattern in [
            ("starter_file", "starter"),
            ("solution_file", "solution"),
            ("test_file", "tests"),
        ]:
            sub = ex_dir / pattern
            if sub.is_dir():
                # Find the first file in the subdirectory
                files = sorted(sub.iterdir())
                if files:
                    ex_entry[key] = f"{phase_dir.name}/{lesson_dir.name}/exercises/{ex_dir.name}/{pattern}/{files[0].name}"
            else:
                # Check for direct file
                candidates = list(ex_dir.glob(f"{pattern}.*"))
                if candidates:
                    ex_entry[key] = f"{phase_dir.name}/{lesson_dir.name}/exercises/{ex_dir.name}/{candidates[0].name}"

        rubric = ex_dir / "rubric.md"
        if rubric.exists():
            ex_entry["rubric_file"] = f"{phase_dir.name}/{lesson_dir.name}/exercises/{ex_dir.name}/rubric.md"

        hints_file = ex_dir / "hints.json"
        if hints_file.exists():
            try:
                hints_data = json.loads(hints_file.read_text(encoding="utf-8"))
                if isinstance(hints_data, list):
                    ex_entry["hints"] = hints_data[:3]
                elif isinstance(hints_data, dict) and "hints" in hints_data:
                    ex_entry["hints"] = hints_data["hints"][:3]
                else:
                    ex_entry["hints"] = []
            except (json.JSONDecodeError, OSError):
                ex_entry["hints"] = []
        else:
            ex_entry["hints"] = []

        exercises.append(ex_entry)

    entry: dict[str, Any] = {
        "id": f"phase-{phase_num:02d}/lesson-{lesson_num:02d}",
        "title": title,
        "phase": phase_num,
        "order": lesson_num,
        "objectives": [],
        "prerequisites": [],
        "estimated_minutes": 30,
        "content_file": content_file,
        "exercises": exercises,
    }
    if quiz_file:
        entry["quiz_file"] = quiz_file
    return entry


# ---------------------------------------------------------------------------
# Manifest sync
# ---------------------------------------------------------------------------

def _sync_manifest(
    curriculum_path: Path,
    manifest_path: Path,
    dry_run: bool = False,
) -> tuple[list[str], list[str], bool]:
    """Synchronise manifest.json with what exists on disk.

    Returns (files_added, files_removed, was_updated).
    """
    # Load existing manifest
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "title": "Learn AI With Grey8",
            "version": "0.1.0",
            "schema": "./schema.json",
            "phases": [],
        }

    # Build index of existing manifest lessons  {lesson_id: (phase_index, lesson_index)}
    existing_ids: dict[str, tuple[int, int]] = {}
    for pi, phase in enumerate(manifest.get("phases", [])):
        for li, lesson in enumerate(phase.get("lessons", [])):
            existing_ids[lesson["id"]] = (pi, li)

    # Scan disk
    disk_phases: dict[int, dict[str, Any]] = {}  # phase_num -> {title, dir, lessons}
    for phase_dir in _discover_phases(curriculum_path):
        phase_num = _parse_phase_number(phase_dir)
        lessons_on_disk: list[dict[str, Any]] = []

        for lesson_dir in _discover_lessons(phase_dir):
            lesson_num = _parse_lesson_number(lesson_dir)
            lesson_id = f"phase-{phase_num:02d}/lesson-{lesson_num:02d}"

            if lesson_id in existing_ids:
                # Keep existing entry (preserves hand-written metadata)
                pi, li = existing_ids[lesson_id]
                lessons_on_disk.append(manifest["phases"][pi]["lessons"][li])
            else:
                # New lesson found on disk — build entry
                lessons_on_disk.append(
                    _build_lesson_entry(phase_dir, lesson_dir, phase_num, lesson_num)
                )

        # Derive phase title from dir name
        phase_slug = phase_dir.name.split("-", 2)
        phase_title = phase_slug[2].replace("-", " ").title() if len(phase_slug) > 2 else f"Phase {phase_num}"

        # Preserve existing phase-level metadata if it exists
        existing_phase = next(
            (p for p in manifest.get("phases", []) if p.get("phase") == phase_num),
            None,
        )
        disk_phases[phase_num] = {
            "phase": phase_num,
            "title": existing_phase["title"] if existing_phase else phase_title,
            "directory": phase_dir.name,
            "lessons": sorted(lessons_on_disk, key=lambda l: l.get("order", 0)),
        }

    # Determine what was added / removed
    disk_ids = set()
    for phase_data in disk_phases.values():
        for lesson in phase_data["lessons"]:
            disk_ids.add(lesson["id"])

    files_added = sorted(disk_ids - set(existing_ids.keys()))
    files_removed = sorted(set(existing_ids.keys()) - disk_ids)
    was_updated = bool(files_added or files_removed)

    if not dry_run and was_updated:
        manifest["phases"] = [
            disk_phases[k] for k in sorted(disk_phases.keys())
        ]
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return files_added, files_removed, was_updated


# ---------------------------------------------------------------------------
# README sync
# ---------------------------------------------------------------------------

_TABLE_START = "<!-- CURRICULUM_TABLE_START -->"
_TABLE_END = "<!-- CURRICULUM_TABLE_END -->"


def _build_curriculum_table(manifest_path: Path) -> str:
    """Generate the markdown curriculum table from the manifest."""
    if not manifest_path.exists():
        return "| Phase | Focus | Lessons | What You Build |\n|-------|-------|---------|----------------|\n| _No data_ | | | |"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    lines: list[str] = [
        "| Phase | Focus | Lessons | What You Build |",
        "|-------|-------|---------|----------------|",
    ]

    for phase in manifest.get("phases", []):
        num = phase["phase"]
        title = phase["title"]
        lessons = phase.get("lessons", [])
        lesson_count = len(lessons)
        topics = ", ".join(l["title"] for l in lessons) if lessons else "--"
        lines.append(f"| {num} | {title} | {lesson_count} | {topics} |")

    return "\n".join(lines)


def _sync_readme(repo_root: Path, manifest_path: Path, dry_run: bool = False) -> bool:
    """Update the curriculum table in README.md between marker comments.

    Returns True if the README was updated.
    """
    readme_path = repo_root / "README.md"
    if not readme_path.exists():
        return False

    text = readme_path.read_text(encoding="utf-8")
    if _TABLE_START not in text or _TABLE_END not in text:
        return False

    new_table = _build_curriculum_table(manifest_path)
    new_section = f"{_TABLE_START}\n{new_table}\n{_TABLE_END}"

    pattern = re.compile(
        re.escape(_TABLE_START) + r".*?" + re.escape(_TABLE_END),
        re.DOTALL,
    )
    new_text = pattern.sub(new_section, text)

    if new_text == text:
        return False

    if not dry_run:
        readme_path.write_text(new_text, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# GETTING_STARTED sync
# ---------------------------------------------------------------------------

def _sync_getting_started(repo_root: Path, manifest_path: Path, dry_run: bool = False) -> bool:
    """Update lesson/phase counts in docs/GETTING_STARTED.md.

    Returns True if the file was updated.
    """
    gs_path = repo_root / "docs" / "GETTING_STARTED.md"
    if not gs_path.exists():
        return False

    text = gs_path.read_text(encoding="utf-8")
    original = text

    # Count phases and lessons from manifest
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        phase_count = len(manifest.get("phases", []))
    else:
        phase_count = 12  # default

    # Update "12 phases" references to actual count
    text = re.sub(r"\b\d{1,2} phases\b", f"{phase_count} phases", text)

    if text == original:
        return False

    if not dry_run:
        gs_path.write_text(text, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Drift / integrity checks
# ---------------------------------------------------------------------------

def _check_integrity(curriculum_path: Path, manifest_path: Path) -> list[str]:
    """Check for drift between manifest and actual files on disk."""
    issues: list[str] = []

    if not manifest_path.exists():
        issues.append("manifest.json does not exist")
        return issues

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for phase in manifest.get("phases", []):
        phase_dir = curriculum_path / phase.get("directory", "")
        if not phase_dir.exists():
            issues.append(f"Phase directory missing: {phase_dir.name}")
            continue

        for lesson in phase.get("lessons", []):
            content_file = lesson.get("content_file", "")
            content_path = curriculum_path / content_file
            if content_file and not content_path.exists():
                issues.append(f"Content file missing: {content_file}")

            quiz_file = lesson.get("quiz_file")
            if quiz_file:
                quiz_path = curriculum_path / quiz_file
                if not quiz_path.exists():
                    issues.append(f"Quiz file missing: {quiz_file}")

            for ex in lesson.get("exercises", []):
                for key in ("starter_file", "solution_file", "test_file", "rubric_file"):
                    fpath = ex.get(key, "")
                    if fpath and not (curriculum_path / fpath).exists():
                        issues.append(f"Exercise file missing: {fpath}")

    return issues


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def sync_all(repo_root: Path, dry_run: bool = False) -> SyncReport:
    """Synchronise manifest, README, and docs with the actual curriculum on disk.

    Parameters
    ----------
    repo_root:
        Root of the learn-ai-with-grey8 repository.
    dry_run:
        If True, detect drift but don't write any changes.

    Returns
    -------
    SyncReport
        Summary of what was (or would be) changed.
    """
    report = SyncReport()

    curriculum_path = repo_root / "curriculum"
    manifest_path = curriculum_path / "manifest.json"

    if not curriculum_path.exists():
        report.issues.append("curriculum/ directory not found")
        return report

    # 1. Sync manifest with disk
    added, removed, updated = _sync_manifest(curriculum_path, manifest_path, dry_run=dry_run)
    report.files_added = added
    report.files_removed = removed
    report.manifest_updated = updated

    # 2. Integrity check (after manifest sync so we check current state)
    report.issues = _check_integrity(curriculum_path, manifest_path)

    # 3. Sync README curriculum table
    report.readme_updated = _sync_readme(repo_root, manifest_path, dry_run=dry_run)

    # 4. Sync GETTING_STARTED
    report.getting_started_updated = _sync_getting_started(repo_root, manifest_path, dry_run=dry_run)

    return report
