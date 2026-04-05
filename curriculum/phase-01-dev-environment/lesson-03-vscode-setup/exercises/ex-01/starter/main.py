"""
Exercise: Talk to a Local AI
==============================
Complete the TODOs below to build a function that sends a prompt to the
Ollama API and returns the model's response text.

When you're finished, run the tests:

    pytest ../tests/test_exercise.py
"""

import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "tinyllama"


def ask_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Send *prompt* to the Ollama API and return the response text.

    Parameters
    ----------
    prompt : str
        The question or instruction to send to the model.
    model : str
        The name of the Ollama model to use (default: tinyllama).

    Returns
    -------
    str
        The text response from the model.
    """
    # TODO 1: Use httpx.post() to send a POST request to OLLAMA_URL.
    #         The JSON body should include three keys:
    #           - "model": the model parameter
    #           - "prompt": the prompt parameter
    #           - "stream": False
    #         Set a timeout of 60 seconds.

    # TODO 2: Parse the JSON response from the API.

    # TODO 3: Return the value of the "response" key from the parsed JSON.

    pass  # Remove this line once you've added your code


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    answer = ask_ollama("What is Python? Answer in one sentence.")
    print(answer)
