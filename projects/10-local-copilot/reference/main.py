"""
Project 10: Local Copilot (Reference)

A code completion endpoint using Flask and a local Ollama LLM.
"""

import requests
from flask import Flask, request, jsonify

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

app = Flask(__name__)


def chat(system_prompt: str, user_message: str) -> str:
    """Send a chat request to Ollama and return the assistant's response."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.RequestException as e:
        return f"# Error: Could not reach Ollama: {e}"


COMPLETION_PROMPT = """You are a code completion engine. You receive incomplete code and must complete it.

Rules:
- Output ONLY the code that comes next (the completion), not the original code
- Write idiomatic, clean code in the specified language
- Keep completions concise: finish the current function or block, do not write an entire program
- Do not include explanations, comments about what you are doing, or markdown formatting
- Do not wrap output in code fences
- If the code looks complete, output a brief logical next step (e.g., a docstring, a test call)

Language: {language}"""


def complete_code(code: str, language: str) -> str:
    """Generate a code completion for the given code prefix."""
    system = COMPLETION_PROMPT.format(language=language)
    completion = chat(system, code)

    # Clean up: remove markdown code fences if the LLM added them
    if completion.startswith("```"):
        lines = completion.split("\n")
        # Remove first line (```lang) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        completion = "\n".join(lines)

    return completion


@app.route("/complete", methods=["POST"])
def complete():
    """Code completion endpoint."""
    data = request.get_json()

    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in request body"}), 400

    code = data["code"]
    language = data.get("language", "python")

    completion = complete_code(code, language)

    return jsonify({
        "completion": completion,
        "language": language,
    })


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "model": MODEL})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
