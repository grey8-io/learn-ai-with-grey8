"""
Project 01: AI Chatbot — Starter Code
======================================
Build a multi-turn CLI chatbot using Ollama's /api/chat endpoint.

Your tasks:
  1. Implement the chat() function to send messages to Ollama
  2. Implement the main loop with conversation history
  3. Add the /quit command to exit gracefully
"""

import requests
from rich.console import Console
from rich.markdown import Markdown

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

console = Console()

# ---------------------------------------------------------------------------
# Conversation history — each entry is {"role": "user"|"assistant", "content": "..."}
# ---------------------------------------------------------------------------
history: list[dict] = []


def chat(user_message: str) -> str:
    """
    Send a message to Ollama and return the assistant's reply.

    TODO:
    1. Append the user's message to `history` with role "user"
    2. POST to f"{OLLAMA_URL}/api/chat" with JSON body:
       {"model": MODEL, "messages": history, "stream": False}
    3. Parse the JSON response to extract the assistant's content
    4. Append the assistant's reply to `history` with role "assistant"
    5. Return the assistant's reply text

    Hint: The response JSON looks like:
      {"message": {"role": "assistant", "content": "..."}}
    """
    pass  # <-- Replace with your implementation


def main() -> None:
    """
    Main loop: read user input, call chat(), display the response.

    TODO:
    1. Print a welcome banner (use console.print with a Panel or simple text)
    2. Loop forever:
       a. Read input from the user (use console.input or built-in input())
       b. If the user types "/quit", print goodbye and break
       c. Call chat() with the user's message
       d. Display the response (try rendering as Markdown for nice formatting)
    3. Handle KeyboardInterrupt (Ctrl+C) to exit gracefully
    """
    pass  # <-- Replace with your implementation


if __name__ == "__main__":
    main()
