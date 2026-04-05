# Building & Testing AI Applications

You have a plan. Now it's time to build -- and more importantly, to build with confidence. Testing AI applications is different from testing traditional software because your main dependency (the LLM) is non-deterministic. In this lesson, you'll learn practical strategies for testing AI apps, mocking LLM responses, and ensuring your code works reliably.

---

## Why Testing AI Apps Is Hard

Traditional unit tests verify exact outputs: `add(2, 3)` should always return `5`. But LLM outputs are:

- **Non-deterministic**: The same prompt can produce different responses each run.
- **Hard to evaluate**: Is "Paris is the capital of France" better than "The capital of France is Paris"?
- **Expensive to run**: Each test that calls a real LLM costs time and potentially money.
- **Slow**: LLM calls take seconds, while unit tests should take milliseconds.

The solution? Test what you *can* control, and mock what you can't.

---

## Testing Strategy for AI Applications

```
          ╱╲
         ╱  ╲        Evaluation Tests  (periodic, slow)
        ╱────╲
       ╱      ╲      Integration Tests (real LLM, slow)
      ╱────────╲
     ╱          ╲    Mock LLM Tests    (fast, controlled)
    ╱────────────╲
   ╱              ╲  Unit Tests        (fastest, most reliable)
  ╱════════════════╲

  Run more tests at the bottom, fewer at the top
```

### Layer 1: Unit Tests (Fast, Deterministic)
Test your pure functions -- prompt builders, parsers, validators, data transformers. These don't call the LLM and should be fast and reliable.

```python
def test_prompt_builder():
    prompt = build_prompt("summarize", "Python is a programming language.")
    assert "summarize" in prompt.lower()
    assert "Python is a programming language." in prompt
```

### Layer 2: Mock LLM Tests (Fast, Controlled)
Replace the real LLM with a mock that returns predetermined responses. This lets you test your application's logic without calling the actual model.

```python
def test_chat_handler_with_mock():
    mock = MockLLM(responses=["Here's a summary: Python is versatile."])
    handler = ChatHandler(llm=mock)
    result = handler.process("Summarize Python")
    assert "summary" in result.lower()
```

### Layer 3: Integration Tests (Slow, Real)
Call the real LLM and verify the response meets criteria (not exact match). Run these less frequently -- in CI, not on every save.

```python
def test_real_llm_responds():
    response = call_ollama("What is 2+2?")
    assert "4" in response
    assert len(response) < 500
```

### Layer 4: Evaluation Tests (Periodic)
Run a suite of prompts and score the responses against reference answers. Track scores over time to detect quality regression.

---

## Mocking LLM Responses

The key to fast, reliable AI tests is mocking. A mock LLM is a function that returns predetermined responses without calling the real model:

```python
def mock_llm(responses):
    """Returns a callable that cycles through predefined responses."""
    index = 0
    def generate(prompt):
        nonlocal index
        result = responses[index % len(responses)]
        index += 1
        return result
    return generate
```

Use mocks to test:
- How your app handles different response formats
- Error handling when the LLM returns garbage
- Edge cases like empty responses or very long outputs
- The flow of your application logic

---

## What to Test in AI Responses

Since you can't test for exact output, test for properties:

| Property | Test Method |
|---|---|
| **Contains keywords** | Check if expected words appear in response |
| **Format compliance** | Verify JSON parses, markdown has headers, etc. |
| **Length bounds** | Response is within acceptable length range |
| **No forbidden content** | Response doesn't contain unwanted patterns |
| **Consistency** | Multiple runs produce similar (not identical) outputs |

```python
def test_response_format():
    response = generate("Return a JSON object with name and age")
    data = json.loads(response)  # Should parse as JSON
    assert "name" in data
    assert "age" in data
```

---

## Evaluation Metrics

For more rigorous testing, compare responses to reference answers:

- **Exact match**: Does the response exactly match the reference? (Strict, rarely useful for LLMs)
- **Keyword overlap**: What fraction of reference keywords appear in the response? (Practical)
- **Length ratio**: Is the response a similar length to the reference? (Catches truncation or verbosity)
- **Semantic similarity**: How close is the meaning? (Requires embeddings -- advanced)

For most projects, keyword overlap and format checking are enough.

---

## CI/CD for AI Applications

Continuous Integration (CI) runs your tests automatically on every code push. For AI apps:

1. **Always run** unit tests and mock LLM tests (fast, free)
2. **Optionally run** integration tests with real LLM (slow, may need GPU)
3. **Periodically run** evaluation suites (weekly or on release branches)

A typical CI pipeline:
```
push code -> lint -> unit tests -> mock tests -> build Docker image -> deploy
```

Integration tests with real LLMs can run nightly or on-demand to save resources.

---

## Documentation Best Practices

Good documentation is part of your project's quality:

- **Code comments**: Explain *why*, not *what*. The code shows what; comments explain reasoning.
- **Docstrings**: Every public function gets a docstring with args, returns, and a brief description.
- **README**: Keep it updated as features change.
- **Architecture doc**: A brief explanation of how components connect (especially for multi-service apps).
- **Prompt documentation**: Document your prompts, why they're structured that way, and what they expect.

---

## Code Review for AI Code

When reviewing AI code (your own or others'), pay special attention to:

1. **Prompt injection risks**: Can user input manipulate the system prompt?
2. **Error handling**: What happens when the LLM times out, returns empty, or returns invalid format?
3. **Token management**: Are prompts efficient? Could they be shorter?
4. **Hardcoded prompts**: Should prompts be configurable or templated?
5. **Missing tests**: Is the LLM interaction tested with mocks?

---

## Your Turn

In the exercise, you'll build an AI testing harness: a `LLMTestHarness` class that tests prompts against various criteria, a `mock_llm` function for deterministic testing, and an `evaluate_quality` function for comparing responses to references.

Let's test!
