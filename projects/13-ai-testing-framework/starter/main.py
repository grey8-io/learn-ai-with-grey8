"""
Project 13: AI Testing Framework (Starter)
Generate pytest unit tests from Python source code using a local LLM.
"""

import sys
from pathlib import Path

import requests

# Ollama API configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


def chat(messages: list[dict]) -> str:
    """Send messages to Ollama and return the assistant's response.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.

    Returns:
        The assistant's response text.
    """
    # TODO: Send a POST request to OLLAMA_URL with:
    #   - "model": MODEL
    #   - "messages": messages
    #   - "stream": False
    # Return the assistant's message content.
    pass


def analyze_code(source_code: str) -> str:
    """Analyze Python source code and describe its structure.

    Args:
        source_code: The Python source code to analyze.

    Returns:
        A description of functions, classes, and their signatures.
    """
    # TODO: Create messages that ask the LLM to analyze the source code:
    #   - System message: "You are a Python code analyzer. List all functions
    #     and classes with their signatures, parameters, and a brief description
    #     of what each one does. Be concise."
    #   - User message: the source code
    #
    # TODO: Call chat() and return the analysis
    pass


def generate_tests(source_code: str, analysis: str) -> str:
    """Generate pytest unit tests for the given source code.

    Args:
        source_code: The original Python source code.
        analysis: The code analysis from analyze_code().

    Returns:
        A string containing valid pytest test code.
    """
    # TODO: Create messages that ask the LLM to generate tests:
    #   - System message: Instruct the LLM to:
    #       * Act as a Python testing expert
    #       * Generate pytest unit tests
    #       * Include tests for normal cases, edge cases, and error cases
    #       * Output ONLY valid Python code (no markdown, no explanations)
    #       * Include the necessary import statement for the module
    #   - User message: Include both the source code and the analysis
    #
    # TODO: Call chat() and return the generated test code
    #
    # Hint: You may need to strip markdown code fences (```python ... ```)
    # from the response if the LLM includes them.
    pass


def main():
    """Main entry point: read a Python file and generate tests for it."""
    # TODO: Step 1 — Check command-line arguments
    # If no file path is provided (len(sys.argv) < 2), print usage and exit:
    #   "Usage: python main.py <path_to_python_file>"

    # TODO: Step 2 — Read the source file
    # Use pathlib.Path to read the file specified in sys.argv[1]
    # Handle FileNotFoundError gracefully

    # TODO: Step 3 — Analyze the code
    # Call analyze_code() and print the analysis

    # TODO: Step 4 — Generate tests
    # Call generate_tests() with the source code and analysis

    # TODO: Step 5 — Write the test file
    # Create a test file named "test_<original_filename>"
    # Write the generated test code to it
    # Print a success message with the output path

    pass


if __name__ == "__main__":
    main()
