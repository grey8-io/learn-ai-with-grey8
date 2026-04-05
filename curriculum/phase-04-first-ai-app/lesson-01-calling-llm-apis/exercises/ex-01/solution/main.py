"""
Exercise: OllamaChat Client — Solution
========================================
"""
import httpx


class OllamaChat:
    """A client for the Ollama chat API."""

    def __init__(self, model: str = "tinyllama", host: str = "http://localhost:11434"):
        """Initialize the chat client.

        Args:
            model: The Ollama model to use.
            host: The Ollama server URL.
        """
        self.model = model
        self.host = host

    def send(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send a single prompt to the model.

        Args:
            prompt: The user's message.
            system_prompt: Optional system message to set behavior.

        Returns:
            The model's response text.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = httpx.post(
            f"{self.host}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def send_with_history(self, messages: list[dict]) -> str:
        """Send a conversation with full message history.

        Args:
            messages: A list of message dicts with 'role' and 'content' keys.

        Returns:
            The model's response text.
        """
        response = httpx.post(
            f"{self.host}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


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
