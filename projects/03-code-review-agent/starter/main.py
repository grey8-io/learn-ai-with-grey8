"""
Project 03: Code Review Agent — Starter Code
==============================================
Parse Python files and get structured code review feedback from a local LLM.

Your tasks:
  1. Implement read_file() to read a Python source file
  2. Implement review_code() to send code to the LLM with a review prompt
  3. Implement main() to handle CLI arguments and orchestrate the review
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
    """
    Read a Python source file and return its contents.

    TODO:
    1. Check that the file exists (filepath.exists())
    2. Check that it's a .py file (filepath.suffix)
    3. Read and return the file contents
    4. Raise FileNotFoundError or ValueError for invalid inputs
    """
    pass  # <-- Replace with your implementation


def review_code(code: str, filename: str) -> str:
    """
    Send code to the LLM for review and return the feedback.

    TODO:
    1. Format the REVIEW_PROMPT with the code
    2. Call chat() with the formatted prompt
    3. Return the response

    Hint: Use REVIEW_PROMPT.format(code=code)
    """
    pass  # <-- Replace with your implementation


def main() -> None:
    """
    CLI entry point: accept file or directory path, perform reviews.

    TODO:
    1. Check sys.argv for a file/directory path argument
    2. If no argument given, print usage and exit
    3. If path is a file, review that single file
    4. If path is a directory, find all .py files and review each
    5. Print the review results with a clear header per file

    Hint for finding .py files in a directory:
      list(Path(path).glob("**/*.py"))
    """
    pass  # <-- Replace with your implementation


if __name__ == "__main__":
    main()
