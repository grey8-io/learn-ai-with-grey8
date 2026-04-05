"""
Exercise: Talk to a Local AI — Solution
=========================================
"""

import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "tinyllama"


def ask_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Send *prompt* to the Ollama API and return the response text."""
    # TODO 1: Use httpx.post() to send a POST request to OLLAMA_URL.
    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=60.0,
    )

    # TODO 2: Parse the JSON response from the API.
    data = response.json()

    # TODO 3: Return the value of the "response" key from the parsed JSON.
    return data["response"]


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    answer = ask_ollama("What is Python? Answer in one sentence.")
    print(answer)
