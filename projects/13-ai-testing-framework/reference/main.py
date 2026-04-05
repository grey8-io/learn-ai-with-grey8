"""
Project 13: AI Testing Framework (Reference)
Generate pytest unit tests from Python source code using a local LLM.
"""

import sys
from pathlib import Path

import requests

# Ollama API configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


def chat(messages: list[dict]) -> str:
    """Send messages to Ollama and return the assistant's response."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "messages": messages, "stream": False},
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def analyze_code(source_code: str) -> str:
    """Analyze Python source code and describe its structure."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a Python code analyzer. List all functions and classes "
                "with their signatures, parameters, and a brief description of what "
                "each one does. Be concise."
            ),
        },
        {
            "role": "user",
            "content": f"Analyze this Python code:\n\n{source_code}",
        },
    ]
    return chat(messages)


def generate_tests(source_code: str, analysis: str) -> str:
    """Generate pytest unit tests for the given source code."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a Python testing expert. Generate comprehensive pytest unit tests. "
                "Include tests for:\n"
                "- Normal/happy path cases\n"
                "- Edge cases (empty input, zero, None)\n"
                "- Error cases where applicable\n\n"
                "Rules:\n"
                "- Output ONLY valid Python code, no markdown fences, no explanations\n"
                "- Use descriptive test function names like test_add_positive_numbers\n"
                "- Include appropriate assertions\n"
                "- Add a brief comment above each test explaining what it checks"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Generate pytest tests for this code:\n\n"
                f"```python\n{source_code}\n```\n\n"
                f"Code analysis:\n{analysis}"
            ),
        },
    ]
    result = chat(messages)

    # Strip markdown code fences if the LLM included them
    if result.startswith("```"):
        lines = result.split("\n")
        # Remove first line (```python) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        result = "\n".join(lines)

    return result


def main():
    """Main entry point: read a Python file and generate tests for it."""
    # Step 1: Check arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_python_file>")
        sys.exit(1)

    # Step 2: Read source file
    source_path = Path(sys.argv[1])
    if not source_path.exists():
        print(f"Error: File not found: {source_path}")
        sys.exit(1)

    source_code = source_path.read_text(encoding="utf-8")
    print(f"Read {len(source_code)} characters from {source_path}")

    # Step 3: Analyze the code
    print("\nAnalyzing code structure...")
    analysis = analyze_code(source_code)
    print(f"\nCode Analysis:\n{analysis}\n")

    # Step 4: Generate tests
    print("Generating tests...")
    test_code = generate_tests(source_code, analysis)

    # Step 5: Write test file
    test_filename = f"test_{source_path.name}"
    test_path = Path(test_filename)
    test_path.write_text(test_code, encoding="utf-8")
    print(f"\nTests written to: {test_path}")
    print(f"Run them with: pytest {test_filename} -v")


if __name__ == "__main__":
    main()
