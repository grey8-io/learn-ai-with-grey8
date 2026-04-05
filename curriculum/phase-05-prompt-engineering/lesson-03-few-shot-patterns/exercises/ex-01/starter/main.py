"""
Exercise: Advanced Prompt Patterns
====================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utility functions for chain-of-thought and few-shot prompting.
"""


def build_chain_of_thought_prompt(question: str, steps_hint: str | None = None) -> str:
    """Build a chain-of-thought prompt that encourages step-by-step reasoning.

    Args:
        question: The question to answer.
        steps_hint: Optional hint about what steps to follow.

    Returns:
        A formatted prompt string.

    Format (without steps_hint):
        Question: {question}

        Let's think step by step.

    Format (with steps_hint):
        Question: {question}

        Let's think step by step. {steps_hint}
    """
    # TODO: Implement this function.
    # 1. Start with "Question: {question}\n\n"
    # 2. Add "Let's think step by step."
    # 3. If steps_hint is provided, append " {steps_hint}" after the step-by-step line.
    # 4. Return the prompt.
    pass


def build_few_shot_prompt(task: str, examples: list[dict], query: str) -> str:
    """Build a few-shot prompt with input/output examples.

    Args:
        task: Description of the task.
        examples: List of dicts with 'input' and 'output' keys.
        query: The actual input to process.

    Returns:
        A formatted prompt string.

    Format:
        Task: {task}

        Input: {example1['input']}
        Output: {example1['output']}

        Input: {example2['input']}
        Output: {example2['output']}

        Input: {query}
        Output:
    """
    # TODO: Implement this function.
    # 1. Start with "Task: {task}\n\n"
    # 2. Loop through examples, adding "Input: {input}\nOutput: {output}\n\n"
    # 3. End with "Input: {query}\nOutput:"
    # 4. Return the prompt.
    pass


def extract_final_answer(cot_response: str) -> str:
    """Extract the final answer from a chain-of-thought response.

    Looks for common answer markers like "Therefore", "Final answer:",
    "The answer is", "In conclusion". Falls back to the last non-empty line.

    Args:
        cot_response: The full chain-of-thought response text.

    Returns:
        The extracted final answer as a string.
    """
    # TODO: Implement this function.
    # 1. Define markers: ["therefore", "final answer:", "the answer is", "in conclusion"]
    # 2. Split the response into lines.
    # 3. Search lines from the bottom up (reversed).
    # 4. For each line, check if any marker appears in the lowercased line.
    # 5. If found, extract the text after the marker, strip whitespace and trailing periods.
    # 6. If no marker found, return the last non-empty line.
    pass


def build_self_consistency_prompts(question: str, n: int = 3) -> list[str]:
    """Build multiple prompt variations for self-consistency voting.

    Creates n slightly different prompts for the same question to enable
    majority-vote answer selection.

    Args:
        question: The question to answer.
        n: Number of prompt variations to generate (default 3).

    Returns:
        A list of n prompt strings, each with a different reasoning prefix.
    """
    # TODO: Implement this function.
    # 1. Define a list of reasoning prefixes, for example:
    #    ["Let's think step by step.",
    #     "Let's solve this carefully.",
    #     "Let's work through this one step at a time.",
    #     "Let's break this down.",
    #     "Let's reason about this."]
    # 2. For i in range(n), pick prefixes[i % len(prefixes)].
    # 3. Build each prompt as "Question: {question}\n\n{prefix}"
    # 4. Return the list of prompts.
    pass


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
