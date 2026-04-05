"""
Project 03: Code Review Agent — Reference Solution
====================================================
Parse Python files and get structured code review feedback from a local LLM.
"""

import sys
from pathlib import Path
import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

REVIEW_PROMPT = """You are an expert Python code reviewer. Review the following code and provide structured feedback.

For each issue found, describe:
- What the issue is
- Where it occurs (approximate line or function)
- Why it matters

Then provide general suggestions for improvement.

Format your response as:

## Issues
- [issue 1]
- [issue 2]

## Suggestions
- [suggestion 1]
- [suggestion 2]

Code to review:
```python
{code}
```"""


def chat(prompt: str) -> str:
    """Send a single prompt to Ollama and return the response."""
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def read_file(filepath: Path) -> str:
    """Read a Python source file and return its contents."""
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if filepath.suffix != ".py":
        raise ValueError(f"Not a Python file: {filepath}")

    return filepath.read_text(encoding="utf-8")


def review_code(code: str, filename: str) -> str:
    """Send code to the LLM for review and return the feedback."""
    prompt = REVIEW_PROMPT.format(code=code)
    return chat(prompt)


def review_file(filepath: Path) -> None:
    """Review a single Python file and print results."""
    print(f"\n{'=' * 60}")
    print(f"  Code Review: {filepath.name}")
    print(f"{'=' * 60}\n")

    try:
        code = read_file(filepath)

        if not code.strip():
            print("  (empty file, skipping)\n")
            return

        print("  Analyzing...\n")
        feedback = review_code(code, filepath.name)
        print(feedback)
        print()

    except (FileNotFoundError, ValueError) as e:
        print(f"  Error: {e}\n")


def main() -> None:
    """CLI entry point: accept file or directory path, perform reviews."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <file.py | directory/>")
        print("  Review a Python file or all .py files in a directory.")
        sys.exit(1)

    target = Path(sys.argv[1])

    if target.is_file():
        # Review single file
        review_file(target)

    elif target.is_dir():
        # Review all .py files in the directory
        py_files = sorted(target.glob("**/*.py"))

        if not py_files:
            print(f"No .py files found in {target}")
            sys.exit(1)

        print(f"Found {len(py_files)} Python file(s) to review.\n")

        for filepath in py_files:
            review_file(filepath)

    else:
        print(f"Path not found: {target}")
        sys.exit(1)


if __name__ == "__main__":
    main()
