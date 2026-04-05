"""
Project 01: AI Chatbot — Reference Solution
=============================================
A multi-turn CLI chatbot using Ollama's /api/chat endpoint with rich formatting.
"""

import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

console = Console()

# Conversation history maintains context across turns
history: list[dict] = []


def chat(user_message: str) -> str:
    """Send a message to Ollama and return the assistant's reply."""
    # Add user message to history
    history.append({"role": "user", "content": user_message})

    # Call Ollama chat API
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": MODEL, "messages": history, "stream": False},
        timeout=120,
    )
    response.raise_for_status()

    # Extract assistant reply
    data = response.json()
    assistant_message = data["message"]["content"]

    # Add assistant reply to history for multi-turn context
    history.append({"role": "assistant", "content": assistant_message})

    return assistant_message


def main() -> None:
    """Main loop: read user input, call chat(), display the response."""
    console.print(
        Panel(
            "[bold green]AI Chatbot[/bold green] powered by Ollama\n"
            "Type your message and press Enter. Type [bold]/quit[/bold] to exit.",
            title="Welcome",
        )
    )

    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()

            # Skip empty input
            if not user_input:
                continue

            # Exit command
            if user_input.lower() == "/quit":
                console.print("[dim]Goodbye![/dim]")
                break

            # Get response from LLM
            with console.status("[dim]Thinking...[/dim]"):
                reply = chat(user_input)

            # Display response as rendered Markdown
            console.print("[bold green]AI:[/bold green]")
            console.print(Markdown(reply))
            console.print()  # blank line for readability

        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except requests.exceptions.ConnectionError:
            console.print(
                "[bold red]Error:[/bold red] Cannot connect to Ollama. "
                "Is it running at {url}?".format(url=OLLAMA_URL)
            )
            break


if __name__ == "__main__":
    main()
