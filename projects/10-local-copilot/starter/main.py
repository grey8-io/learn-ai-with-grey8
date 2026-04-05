"""
Project 10: Local Copilot (Starter)

A code completion endpoint using Flask and a local Ollama LLM.

Your task: implement the chat helper, code completion logic, and Flask route.
"""

import requests
from flask import Flask, request, jsonify

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

app = Flask(__name__)


def chat(system_prompt: str, user_message: str) -> str:
    """Send a chat request to Ollama and return the assistant's response.

    Args:
        system_prompt: Instructions for the LLM's behavior.
        user_message: The user's input (code context).

    Returns:
        The assistant's response text.
    """
    # TODO: Send a POST to OLLAMA_URL/api/chat with model, messages, stream=False.
    # TODO: Return the response content.
    # TODO: Handle connection errors gracefully.
    pass


def complete_code(code: str, language: str) -> str:
    """Generate a code completion for the given code prefix.

    Args:
        code: The existing code that needs completion.
        language: The programming language (e.g., "python", "javascript").

    Returns:
        The suggested code completion (continuation only, not the original code).
    """
    # TODO: Create a system prompt that instructs the LLM to:
    #   1. Act as a code completion engine
    #   2. Complete the given code in the specified language
    #   3. Return ONLY the completion (the new code to add), not the original code
    #   4. Keep completions concise and idiomatic
    #   5. Do not include explanations, just code
    #
    # TODO: Call chat() with the system prompt and the code as user message.
    # TODO: Return the completion text.
    pass


@app.route("/complete", methods=["POST"])
def complete():
    """Code completion endpoint.

    Expects JSON: {"code": "...", "language": "python"}
    Returns JSON: {"completion": "...", "language": "..."}
    """
    # TODO: Parse the JSON request body.
    # TODO: Validate that "code" is present; return 400 error if missing.
    # TODO: Get "language" with a default of "python".
    # TODO: Call complete_code() with the code and language.
    # TODO: Return a JSON response with "completion" and "language".
    #
    # Hint: Use request.get_json() to parse, jsonify() to respond.
    # Hint: Return errors with jsonify({"error": "..."}), 400
    pass


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "model": MODEL})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
