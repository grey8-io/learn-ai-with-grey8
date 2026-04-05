# Few-Shot Patterns & Chain of Thought

Some prompts work dramatically better than others. In this lesson, you'll learn the two most powerful prompting techniques: **few-shot prompting** (showing examples) and **chain-of-thought** (step-by-step reasoning). These techniques can turn a mediocre AI response into an excellent one, often without changing the model at all.

---

## The Prompting Spectrum

There are three levels of example-based prompting:

```
  Zero-Shot              One-Shot              Few-Shot
  ┌──────────┐          ┌──────────┐          ┌──────────┐
  │ No        │          │ 1 example │          │ 3-5      │
  │ examples  │          │ shown     │          │ examples │
  └──────────┘          └──────────┘          └──────────┘
  "Classify this         "Example:              "Example 1: ...
   review as              'Great!' → positive    Example 2: ...
   positive or            Now classify:"         Example 3: ...
   negative"                                     Now classify:"

  Consistency: ★☆☆       Consistency: ★★☆       Consistency: ★★★
```

- **Zero-shot**: No examples. Just ask the question.
- **One-shot**: One example before the question.
- **Few-shot**: Multiple examples (typically 2-5) before the question.

### Zero-Shot
```
Classify this review as POSITIVE or NEGATIVE: "The battery lasts forever!"
```

The model *might* get this right, but it also might respond with a full paragraph instead of just the label.

### One-Shot
```
Classify this review:
"I love this phone!" -> POSITIVE

Now classify: "The battery lasts forever!"
```

Better -- the model sees the expected format.

### Few-Shot
```
Classify this review:
"I love this phone!" -> POSITIVE
"Terrible experience." -> NEGATIVE
"Works as described." -> POSITIVE

Now classify: "The battery lasts forever!"
```

Best -- the model has multiple examples showing the pattern, including edge cases. Few-shot prompting is one of the most reliable ways to get consistent output.

---

## When to Use Few-Shot

Few-shot works best when:

- You need a **specific output format** (labels, JSON, structured text)
- The task has **clear input/output patterns** (classification, translation, extraction)
- **Zero-shot gives inconsistent results** (sometimes right, sometimes wrong format)
- You want the model to handle **edge cases** correctly

Few-shot is less useful when:
- The task requires deep reasoning (use chain-of-thought instead)
- You need creative or open-ended responses
- The examples would be too long to fit in the context window

---

## Chain-of-Thought (CoT) Prompting

Chain-of-thought prompting asks the model to "think step by step" before giving a final answer. This simple technique dramatically improves performance on reasoning tasks.

### Without CoT
```
Q: A store has 23 apples. They sell 7, then receive 15 more. How many apples?
A: 31
```

The model jumps straight to an answer -- and often gets it wrong on harder problems.

### With CoT
```
Q: A store has 23 apples. They sell 7, then receive 15 more. How many apples?
A: Let's think step by step.
   1. Start with 23 apples.
   2. Sell 7: 23 - 7 = 16 apples.
   3. Receive 15: 16 + 15 = 31 apples.
   Therefore, the answer is 31.
```

By forcing the model to show its work, it makes fewer mistakes. The magic phrase is **"Let's think step by step."** -- it's simple but research has shown it significantly improves accuracy.

```
  Without CoT:                    With CoT:
  Q: "15% tip on $85?"           Q: "15% tip on $85? Think step by step."
  A: "$12.50" ✗ (wrong)          A: "Step 1: 10% of $85 = $8.50
                                     Step 2: 5% = $8.50 / 2 = $4.25
                                     Step 3: $8.50 + $4.25 = $12.75" ✓

  Model jumped to answer          Model used reasoning as scratchpad
```

---

## Why Does CoT Work?

LLMs generate text one token at a time. When you ask for a direct answer, the model has to "compute" the result in a single step. When you ask it to reason step by step, each step of reasoning becomes part of the context for the next step. The model essentially uses its own output as a scratchpad.

This is why CoT helps most with:
- **Math problems** (multi-step calculations)
- **Logic puzzles** (if/then reasoning)
- **Code debugging** (tracing through execution)
- **Complex analysis** (considering multiple factors)

---

## Extracting the Final Answer

When using CoT, the model produces a lot of reasoning text. You need to extract just the final answer. Common patterns to look for:

- "Therefore, the answer is X"
- "Final answer: X"
- "The result is X"
- "In conclusion, X"

```python
def extract_final_answer(cot_response):
    """Extract the final answer from a chain-of-thought response."""
    markers = ["therefore", "final answer:", "the answer is", "in conclusion"]
    lines = cot_response.strip().split('\n')

    for line in reversed(lines):
        lower = line.lower().strip()
        for marker in markers:
            if marker in lower:
                # Extract text after the marker
                idx = lower.index(marker) + len(marker)
                return line.strip()[idx:].strip().rstrip('.')
    # Fallback: return the last non-empty line
    for line in reversed(lines):
        if line.strip():
            return line.strip()
    return ""
```

---

## Self-Consistency: Voting on Answers

What if you're not sure the model's reasoning is correct? **Self-consistency** runs the same question multiple times with slightly different prompts and takes the majority answer.

```python
prompts = [
    "Let's think step by step. " + question,
    "Let's solve this carefully. " + question,
    "Let's work through this one step at a time. " + question,
]
# Send each prompt, extract answers, take the most common one.
```

This technique trades speed for accuracy -- useful when correctness matters more than latency.

---

## Combining Few-Shot and CoT

The most powerful technique combines both: show few-shot examples that include chain-of-thought reasoning.

```
Q: If a train travels 60 mph for 2.5 hours, how far does it go?
A: Let's think step by step.
   Distance = speed * time = 60 * 2.5 = 150 miles.
   Therefore, the answer is 150 miles.

Q: If a car travels 45 mph for 3 hours, how far does it go?
A:
```

The model learns both the reasoning pattern AND the output format from the examples.

---

## Building Prompt Patterns in Code

In practice, you'll want reusable functions for these patterns:

```python
def build_chain_of_thought_prompt(question):
    return f"Question: {question}\n\nLet's think step by step."

def build_few_shot_prompt(task, examples, query):
    prompt = f"Task: {task}\n\n"
    for ex in examples:
        prompt += f"Input: {ex['input']}\nOutput: {ex['output']}\n\n"
    prompt += f"Input: {query}\nOutput:"
    return prompt
```

These utility functions make your codebase cleaner and your prompts more consistent.

---

## Choosing the Right Technique

| Task Type | Recommended Approach |
|---|---|
| Classification | Few-shot with label examples |
| Math / Logic | Chain-of-thought |
| Format-specific output | Few-shot with format examples |
| Complex reasoning | Few-shot + CoT combined |
| High-stakes accuracy | Self-consistency (multiple runs) |

---

## Your Turn

In the exercise, you'll build four functions: a chain-of-thought prompt builder, a few-shot prompt builder, a CoT response parser, and a self-consistency prompt generator. These are the building blocks of advanced prompt engineering.

Let's think step by step!
