"""
Project 11: AI Email Assistant (Reference)
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
    """Send messages to Ollama and return the assistant's response."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "messages": messages, "stream": False},
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def generate_email(notes: str, tone: str) -> tuple[str, list[dict]]:
    """Generate a professional email from rough notes.

    Returns the email text and the full conversation history for refinement.
    """
    messages = [
        {
            "role": "system",
            "content": (
                f"You are a professional email writer. Write emails in a {tone} tone. "
                "Transform the user's bullet points or rough notes into a well-structured email. "
                "Always include: a subject line (prefixed with 'Subject:'), an appropriate greeting, "
                "a clear body organized in paragraphs, and a professional sign-off. "
                "Output only the email — no extra commentary."
            ),
        },
        {
            "role": "user",
            "content": f"Write an email from these notes:\n\n{notes}",
        },
    ]
    reply = chat(messages)
    # Add assistant reply to conversation for multi-turn context
    messages.append({"role": "assistant", "content": reply})
    return reply, messages


def refine_email(conversation: list[dict], feedback: str) -> str:
    """Refine a previously generated email based on user feedback."""
    conversation.append(
        {
            "role": "user",
            "content": (
                f"Please revise the email based on this feedback: {feedback}\n"
                "Output only the revised email — no extra commentary."
            ),
        }
    )
    reply = chat(conversation)
    conversation.append({"role": "assistant", "content": reply})
    return reply


def main():
    """Main CLI loop for the email assistant."""
    console.print(Panel("[bold]AI Email Assistant[/bold]\nTurn rough notes into polished emails", style="blue"))

    # Step 1: Collect notes
    console.print("[cyan]Enter your bullet points or rough notes (press Enter twice to finish):[/cyan]")
    lines = []
    while True:
        line = console.input("")
        if line == "":
            if lines:
                break
            continue
        lines.append(line)
    notes = "\n".join(lines)

    # Step 2: Choose tone
    tone = Prompt.ask(
        "Choose a tone",
        choices=["professional", "friendly", "formal", "casual"],
        default="professional",
    )

    # Step 3: Generate initial draft
    with console.status("[bold green]Generating email draft..."):
        email, conversation = generate_email(notes, tone)

    console.print(Panel(email, title="Generated Email", border_style="green"))

    # Step 4: Iterative refinement loop
    while True:
        action = Prompt.ask(
            "Refine this email? Enter feedback or type 'done' to finish",
            default="done",
        )
        if action.lower() == "done":
            break

        with console.status("[bold green]Refining email..."):
            email = refine_email(conversation, action)

        console.print(Panel(email, title="Revised Email", border_style="yellow"))

    console.print(Panel(email, title="Final Email", border_style="bold green"))
    console.print("[green]Done! Copy your email above.[/green]")


if __name__ == "__main__":
    main()
