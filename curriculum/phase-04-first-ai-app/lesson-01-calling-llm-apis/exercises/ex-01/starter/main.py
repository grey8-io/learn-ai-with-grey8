"""
Exercise: OllamaChat Client
==============================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a reusable class for communicating with the Ollama chat API.
"""
import httpx


# TODO: Build an `OllamaChat` class with:
#
# __init__(self, model: str = "tinyllama", host: str = "http://localhost:11434")
#   - Store model and host as instance attributes
#
# send(self, prompt: str, system_prompt: str | None = None) -> str
#   - Build a messages list:
#     * If system_prompt is provided, add {"role": "system", "content": system_prompt}
#     * Add {"role": "user", "content": prompt}
#   - POST to {self.host}/api/chat with JSON body:
#     {"model": self.model, "messages": messages, "stream": False}
#   - Set timeout=60
#   - Call response.raise_for_status()
#   - Return response.json()["message"]["content"]
#
# send_with_history(self, messages: list[dict]) -> str
#   - Takes a pre-built list of message dicts (with role/content keys)
#   - POST to {self.host}/api/chat with JSON body:
#     {"model": self.model, "messages": messages, "stream": False}
#   - Set timeout=60
#   - Call response.raise_for_status()
#   - Return response.json()["message"]["content"]


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    chat = OllamaChat()
    response = chat.send("Say hello in one word.")
    print(f"Response: {response}")

    history = [
        {"role": "system", "content": "You are a pirate. Speak like one."},
        {"role": "user", "content": "What's the weather like?"},
    ]
    response = chat.send_with_history(history)
    print(f"Pirate says: {response}")
