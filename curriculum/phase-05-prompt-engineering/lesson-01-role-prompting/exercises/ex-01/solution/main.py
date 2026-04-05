"""
Exercise: Prompt Engineering Utilities — Solution
===================================================
"""


def create_system_prompt(role: str, expertise: str, tone: str, constraints: str) -> str:
    """Create a formatted system prompt from components.

    Args:
        role: The role the AI should assume.
        expertise: The AI's area of expertise.
        tone: The communication style.
        constraints: Limitations or rules.

    Returns:
        A formatted system prompt string combining all components.
    """
    return (
        f"You are a {role}.\n"
        f"You specialize in {expertise}.\n"
        f"Tone: {tone}.\n"
        f"Constraints: {constraints}."
    )


def create_few_shot_prompt(task_description: str, examples: list[dict], query: str) -> str:
    """Create a few-shot prompt with examples.

    Args:
        task_description: What the AI should do.
        examples: List of dicts with 'input' and 'output' keys.
        query: The actual input to process.

    Returns:
        A formatted prompt string with task, examples, and query.
    """
    prompt = f"Task: {task_description}\n\nExamples:\n"
    for example in examples:
        prompt += f"Input: {example['input']}\nOutput: {example['output']}\n\n"
    prompt += f"Now perform the task:\nInput: {query}\nOutput:"
    return prompt


def validate_prompt(prompt: str, max_tokens: int = 500) -> dict:
    """Validate a prompt before sending to an LLM.

    Args:
        prompt: The prompt string to validate.
        max_tokens: Maximum estimated tokens allowed.

    Returns:
        A dict with valid, issues, and estimated_tokens.
    """
    issues = []
    estimated_tokens = len(prompt) // 4

    if not prompt.strip():
        issues.append("Prompt is empty")

    if estimated_tokens > max_tokens:
        issues.append(f"Prompt exceeds token limit ({estimated_tokens} > {max_tokens})")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "estimated_tokens": estimated_tokens,
    }


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
