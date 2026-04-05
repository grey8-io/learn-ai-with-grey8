#!/usr/bin/env python3
"""Generate a compact curriculum index from content.md files.

Produces curriculum/curriculum_index.json — a lightweight summary of every
lesson (title, one-line summary, key concepts, prerequisites) that the tutor
engine can inject into the LLM context for cross-lesson awareness.

Run during setup: python scripts/generate_curriculum_index.py
Regenerates automatically via: ace sync (if wired) or setup.sh
"""

import json
import re
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent / "curriculum"
MANIFEST_PATH = CURRICULUM_DIR / "manifest.json"
OUTPUT_PATH = CURRICULUM_DIR / "curriculum_index.json"


def extract_summary(content: str, max_words: int = 25) -> str:
    """Extract a one-line summary from lesson content.

    Takes the first meaningful paragraph (skipping the title and horizontal rules).
    """
    lines = content.strip().split("\n")
    for line in lines:
        line = line.strip()
        # Skip headings, empty lines, horizontal rules, code blocks
        if not line or line.startswith("#") or line.startswith("---") or line.startswith("```"):
            continue
        # Skip very short lines (likely formatting)
        if len(line) < 30:
            continue
        # Found a real paragraph — take first N words
        words = line.split()[:max_words]
        summary = " ".join(words)
        if len(words) == max_words:
            summary += "..."
        return summary
    return "No summary available."


def extract_key_concepts(content: str) -> list[str]:
    """Extract key concepts from H2/H3 headings in the lesson content."""
    concepts = []
    for match in re.finditer(r"^#{2,3}\s+(.+)$", content, re.MULTILINE):
        heading = match.group(1).strip()
        # Skip generic headings
        if heading.lower() in ("your turn", "summary", "putting it together", "next steps"):
            continue
        concepts.append(heading)
    return concepts[:8]  # cap at 8 key concepts


def main():
    if not MANIFEST_PATH.exists():
        print(f"ERROR: Manifest not found at {MANIFEST_PATH}")
        print("Run 'ace sync' first to generate the manifest.")
        return

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    index = {"generated": True, "lessons": []}

    for phase in manifest["phases"]:
        for lesson in phase["lessons"]:
            lesson_id = lesson["id"]
            content_file = CURRICULUM_DIR / lesson.get("content_file", "")

            content = ""
            if content_file.exists():
                content = content_file.read_text(encoding="utf-8")

            summary = extract_summary(content)
            concepts = extract_key_concepts(content)

            index["lessons"].append({
                "id": lesson_id,
                "phase": phase["phase"],
                "title": lesson["title"],
                "summary": summary,
                "concepts": concepts,
                "prerequisites": lesson.get("prerequisites", []),
                "estimated_minutes": lesson.get("estimated_minutes", 0),
            })

    OUTPUT_PATH.write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Generated curriculum index: {OUTPUT_PATH}")
    print(f"  {len(index['lessons'])} lessons indexed")


if __name__ == "__main__":
    main()
