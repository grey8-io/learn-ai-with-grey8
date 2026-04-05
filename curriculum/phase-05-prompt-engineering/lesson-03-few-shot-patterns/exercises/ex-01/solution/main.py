"""
Exercise: Advanced Prompt Patterns — Solution
===============================================
"""


def build_chain_of_thought_prompt(question: str, steps_hint: str | None = None) -> str:
    """Build a chain-of-thought prompt that encourages step-by-step reasoning.

    Args:
        question: The question to answer.
        steps_hint: Optional hint about what steps to follow.

    Returns:
        A formatted prompt string.
    """
    prompt = f"Question: {question}\n\nLet's think step by step."
    if steps_hint:
        prompt += f" {steps_hint}"
    return prompt


def build_few_shot_prompt(task: str, examples: list[dict], query: str) -> str:
    """Build a few-shot prompt with input/output examples.

    Args:
        task: Description of the task.
        examples: List of dicts with 'input' and 'output' keys.
        query: The actual input to process.

    Returns:
        A formatted prompt string.
    """
    prompt = f"Task: {task}\n\n"
    for example in examples:
        prompt += f"Input: {example['input']}\nOutput: {example['output']}\n\n"
    prompt += f"Input: {query}\nOutput:"
    return prompt


def extract_final_answer(cot_response: str) -> str:
    """Extract the final answer from a chain-of-thought response.

    Args:
        cot_response: The full chain-of-thought response text.

    Returns:
        The extracted final answer as a string.
    """
    markers = ["therefore", "final answer:", "the answer is", "in conclusion"]
    lines = cot_response.strip().split('\n')

    for line in reversed(lines):
        lower = line.lower().strip()
        for marker in markers:
            if marker in lower:
                idx = lower.index(marker) + len(marker)
                answer = line.strip()[idx:].strip().rstrip('.')
                # Remove leading punctuation like commas or colons
                answer = answer.lstrip(',: ').strip()
                return answer

    # Fallback: return the last non-empty line
    for line in reversed(lines):
        if line.strip():
            return line.strip()
    return ""


def build_self_consistency_prompts(question: str, n: int = 3) -> list[str]:
    """Build multiple prompt variations for self-consistency voting.

    Args:
        question: The question to answer.
        n: Number of prompt variations to generate.

    Returns:
        A list of n prompt strings with different reasoning prefixes.
    """
    prefixes = [
        "Let's think step by step.",
        "Let's solve this carefully.",
        "Let's work through this one step at a time.",
        "Let's break this down.",
        "Let's reason about this.",
    ]

    prompts = []
    for i in range(n):
        prefix = prefixes[i % len(prefixes)]
        prompts.append(f"Question: {question}\n\n{prefix}")
    return prompts


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cot = build_chain_of_thought_prompt("What is 23 + 45?")
    print("CoT Prompt:")
    print(cot)
    print()

    cot_with_hint = build_chain_of_thought_prompt(
        "What is 23 + 45?",
        steps_hint="First add the tens, then the ones."
    )
    print("CoT with hint:")
    print(cot_with_hint)
    print()

    few_shot = build_few_shot_prompt(
        task="Translate English to French",
        examples=[
            {"input": "Hello", "output": "Bonjour"},
            {"input": "Goodbye", "output": "Au revoir"},
        ],
        query="Thank you",
    )
    print("Few-Shot Prompt:")
    print(few_shot)
    print()

    response = """Let's think step by step.
1. 23 + 45
2. 20 + 40 = 60
3. 3 + 5 = 8
4. 60 + 8 = 68
Therefore, the answer is 68."""
    answer = extract_final_answer(response)
    print(f"Extracted answer: {answer}")
    print()

    prompts = build_self_consistency_prompts("What is 15% of 200?", n=3)
    print("Self-consistency prompts:")
    for i, p in enumerate(prompts):
        print(f"  [{i}] {p[:60]}...")
