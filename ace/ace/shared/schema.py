"""Schema utilities for validating curriculum content."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


def _schema_dir() -> Path:
    """Return the path to the curriculum schema directory."""
    return Path(__file__).resolve().parent.parent.parent.parent / "curriculum"


def load_schema(name: str = "schema.json") -> dict[str, Any]:
    """Load a JSON schema from the curriculum directory.

    Parameters
    ----------
    name:
        Filename of the schema inside ``curriculum/``.

    Returns
    -------
    dict
        Parsed JSON schema.
    """
    schema_path = _schema_dir() / name
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_lesson(data: dict[str, Any]) -> list[str]:
    """Validate lesson metadata against the curriculum schema.

    Returns a list of validation error messages (empty if valid).
    """
    try:
        schema = load_schema()
    except FileNotFoundError:
        return ["Schema file not found — skipping JSON schema validation."]

    lesson_schema = schema.get("definitions", {}).get("lesson", schema)
    errors: list[str] = []
    for error in jsonschema.Draft7Validator(lesson_schema).iter_errors(data):
        errors.append(f"{error.json_path}: {error.message}")
    return errors


def validate_exercise(data: dict[str, Any]) -> list[str]:
    """Validate exercise metadata against the curriculum schema.

    Returns a list of validation error messages (empty if valid).
    """
    try:
        schema = load_schema()
    except FileNotFoundError:
        return ["Schema file not found — skipping JSON schema validation."]

    exercise_schema = schema.get("definitions", {}).get("exercise", schema)
    errors: list[str] = []
    for error in jsonschema.Draft7Validator(exercise_schema).iter_errors(data):
        errors.append(f"{error.json_path}: {error.message}")
    return errors
