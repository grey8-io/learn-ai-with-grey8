"""
Project 11: AI Email Assistant (Starter)
Generate professional emails from bullet points using a local LLM.
"""

import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Ollama API configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

console = Console()


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
    # Parse the JSON response and return the assistant's message content.
    # Hint: response.json()["message"]["content"]
    pass


def generate_email(notes: str, tone: str) -> str:
    """Generate a professional email from rough notes.

    Args:
        notes: Bullet points or rough notes from the user.
        tone: Desired tone (professional, friendly, formal, casual).

    Returns:
        The generated email text.
    """
    # TODO: Create a system message that instructs the LLM to:
    #   - Act as a professional email writer
    #   - Use the specified tone
    #   - Transform bullet points into a well-structured email
    #   - Include a subject line, greeting, body, and sign-off
    #
    # TODO: Create a user message containing the notes
    #
    # TODO: Call chat() with both messages and return the result
    pass


def refine_email(conversation: list[dict], feedback: str) -> str:
    """Refine a previously generated email based on user feedback.

    Args:
        conversation: The full conversation history so far.
        feedback: User's refinement instructions (e.g., "make it shorter").

    Returns:
        The refined email text.
    """
    # TODO: Append the user's feedback as a new message to the conversation
    # The feedback should ask the LLM to revise the email based on the instruction
    #
    # TODO: Call chat() with the updated conversation and return the result
    #
    # Hint: The conversation already contains the system prompt and previous
    # messages, so the LLM has full context of what was generated before.
    pass


def main():
    """Main CLI loop for the email assistant."""
    console.print(Panel("AI Email Assistant", style="bold blue"))

    # TODO: Step 1 — Prompt the user for their bullet points / rough notes
    # Use rich's Prompt.ask() or console.input() to get multi-line input
    # Hint: You could ask the user to type notes and press Enter twice to finish,
    # or just accept a single paragraph of notes.

    # TODO: Step 2 — Ask the user to choose a tone
    # Options: professional, friendly, formal, casual

    # TODO: Step 3 — Call generate_email() and display the draft
    # Use console.print() with a Panel to show the email nicely

    # TODO: Step 4 — Enter a refinement loop
    # Keep asking the user if they want to refine the email
    # If yes, get their feedback and call refine_email()
    # If no (or they type "done"), exit the loop
    #
    # Remember to maintain the conversation history list so the LLM
    # has context of all previous drafts and feedback.

    console.print("[green]Done! Copy your email above.[/green]")


if __name__ == "__main__":
    main()
