"""
Exercise: CLI Assistant Utilities — Solution
==============================================
"""
import json


def create_system_prompt(name: str, personality: str) -> str:
    """Create a system prompt for the AI assistant.

    Args:
        name: The assistant's name.
        personality: A description of the assistant's personality.

    Returns:
        A formatted system prompt string.
    """
    return f"You are {name}, an AI assistant. {personality} Keep responses concise and helpful."


def format_history(messages: list[dict]) -> str:
    """Format conversation history for display.

    Args:
        messages: A list of message dicts with 'role' and 'content' keys.

    Returns:
        A formatted string with user and assistant messages, one per line.
    """
    lines = []
    for msg in messages:
        if msg["role"] == "user":
            lines.append(f"You: {msg['content']}")
        elif msg["role"] == "assistant":
            lines.append(f"AI: {msg['content']}")
    return "\n".join(lines)


def save_conversation(messages: list[dict], filepath: str) -> None:
    """Save conversation history to a JSON file.

    Args:
        messages: The conversation messages to save.
        filepath: The file path to save to.
    """
    with open(filepath, "w") as f:
        json.dump(messages, f, indent=2)


def load_conversation(filepath: str) -> list[dict]:
    """Load conversation history from a JSON file.

    Args:
        filepath: The file path to load from.

    Returns:
        The loaded messages list, or an empty list if the file doesn't exist.
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    system = create_system_prompt("Aria", "You are friendly and knowledgeable.")
    print(f"System prompt: {system}\n")

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help you today?"},
        {"role": "user", "content": "Tell me about Python."},
        {"role": "assistant", "content": "Python is a versatile programming language!"},
    ]
    print("Conversation:")
    print(format_history(messages))

    save_conversation(messages, "test_conversation.json")
    print("\nSaved conversation.")

    loaded = load_conversation("test_conversation.json")
    print(f"Loaded {len(loaded)} messages.")
