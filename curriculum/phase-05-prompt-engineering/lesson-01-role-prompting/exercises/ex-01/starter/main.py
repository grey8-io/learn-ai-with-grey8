"""
Exercise: Prompt Engineering Utilities
========================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utility functions for crafting and validating prompts.
"""


def create_system_prompt(role: str, expertise: str, tone: str, constraints: str) -> str:
    """Create a formatted system prompt from components.

    Args:
        role: The role the AI should assume (e.g., "Python tutor").
        expertise: The AI's area of expertise (e.g., "beginner Python concepts").
        tone: The communication style (e.g., "friendly and encouraging").
        constraints: Limitations or rules (e.g., "Keep responses under 100 words").

    Returns:
        A formatted system prompt string combining all components.

    The format should be:
        You are a {role}.
        You specialize in {expertise}.
        Tone: {tone}.
        Constraints: {constraints}.
    """
    # TODO: Implement this function.
    # Combine role, expertise, tone, and constraints into a single formatted string.
    # Each component should be on its own line.
    # Return the assembled prompt string.
    pass


def create_few_shot_prompt(task_description: str, examples: list[dict], query: str) -> str:
    """Create a few-shot prompt with examples.

    Args:
        task_description: What the AI should do (e.g., "Classify sentiment").
        examples: List of dicts with 'input' and 'output' keys.
        query: The actual input to process.

    Returns:
        A formatted prompt string with task, examples, and query.

    The format should be:
        Task: {task_description}

        Examples:
        Input: {example['input']}
        Output: {example['output']}

        Input: {example['input']}
        Output: {example['output']}

        Now perform the task:
        Input: {query}
        Output:
    """
    # TODO: Implement this function.
    # 1. Start with "Task: {task_description}\n\nExamples:\n"
    # 2. Loop through examples and add "Input: {input}\nOutput: {output}\n\n"
    # 3. End with "Now perform the task:\nInput: {query}\nOutput:"
    # 4. Return the assembled string.
    pass


def validate_prompt(prompt: str, max_tokens: int = 500) -> dict:
    """Validate a prompt before sending to an LLM.

    Args:
        prompt: The prompt string to validate.
        max_tokens: Maximum estimated tokens allowed (default 500).

    Returns:
        A dict with:
            - valid (bool): True if the prompt passes all checks.
            - issues (list[str]): List of issue descriptions (empty if valid).
            - estimated_tokens (int): Estimated token count (chars / 4).

    Checks:
        1. Prompt is not empty or whitespace-only -> issue: "Prompt is empty"
        2. Estimated tokens <= max_tokens -> issue: "Prompt exceeds token limit ({estimated} > {max_tokens})"
    """
    # TODO: Implement this function.
    # 1. Initialize issues as an empty list.
    # 2. Check if prompt is empty or whitespace-only (use .strip()).
    # 3. Estimate tokens as len(prompt) // 4.
    # 4. Check if estimated tokens exceed max_tokens.
    # 5. Return the dict with valid, issues, and estimated_tokens.
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    prompt = create_system_prompt(
        role="Python tutor",
        expertise="beginner Python programming",
        tone="friendly and encouraging",
        constraints="Keep responses under 100 words",
    )
    print("System Prompt:")
    print(prompt)
    print()

    few_shot = create_few_shot_prompt(
        task_description="Classify the sentiment as POSITIVE, NEGATIVE, or NEUTRAL",
        examples=[
            {"input": "I love this!", "output": "POSITIVE"},
            {"input": "This is terrible.", "output": "NEGATIVE"},
        ],
        query="It works fine.",
    )
    print("Few-Shot Prompt:")
    print(few_shot)
    print()

    result = validate_prompt(prompt)
    print(f"Validation: {result}")
