"""
Exercise: CLI Assistant Utilities
====================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build the utility functions for an interactive CLI AI assistant.
"""
import json


# TODO 1: Write a function called `create_system_prompt` that:
#          - Takes two parameters: name (str) and personality (str)
#          - Returns a string in the format:
#            "You are {name}, an AI assistant. {personality} Keep responses concise and helpful."
#          - Example: create_system_prompt("Aria", "You are friendly.")
#            -> "You are Aria, an AI assistant. You are friendly. Keep responses concise and helpful."


# TODO 2: Write a function called `format_history` that:
#          - Takes one parameter: messages (list[dict])
#          - Each dict has "role" and "content" keys
#          - Format user messages as "You: {content}"
#          - Format assistant messages as "AI: {content}"
#          - Skip system messages (don't include them)
#          - Return a single string with entries separated by newlines
#          - If no user/assistant messages exist, return an empty string


# TODO 3: Write a function called `save_conversation` that:
#          - Takes two parameters: messages (list[dict]) and filepath (str)
#          - Saves the messages list to the filepath as JSON with indent=2
#          - Does not return anything


# TODO 4: Write a function called `load_conversation` that:
#          - Takes one parameter: filepath (str)
#          - Loads and returns the messages list from the JSON file
#          - If the file doesn't exist, return an empty list
#          - Use try/except FileNotFoundError


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
