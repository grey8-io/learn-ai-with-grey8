"""
Exercise: AI Testing Utilities
================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utilities for testing AI applications.
"""

import json


class LLMTestHarness:
    """A test harness for evaluating LLM-powered functions."""

    def __init__(self, generate_fn):
        """Initialize the test harness.

        Args:
            generate_fn: A callable that takes a prompt (str) and returns a response (str).
                         This can be a real LLM function or a mock.
        """
        # TODO: Store generate_fn as an instance attribute.
        pass

    def test_prompt(
        self,
        prompt: str,
        expected_keywords: list[str] | None = None,
        unexpected_keywords: list[str] | None = None,
        max_length: int | None = None,
    ) -> dict:
        """Test a single prompt against criteria.

        Args:
            prompt: The prompt to send.
            expected_keywords: Words that should appear in the response.
            unexpected_keywords: Words that should NOT appear in the response.
            max_length: Maximum allowed response length.

        Returns:
            A dict with:
                - passed (bool): True if all checks pass.
                - response (str): The actual response.
                - checks (list[dict]): Each check as {check: str, passed: bool, details: str}.
        """
        # TODO: Implement this method.
        # 1. Call self.generate_fn(prompt) to get the response.
        # 2. Run each check (expected_keywords, unexpected_keywords, max_length).
        # 3. Build the checks list and determine overall pass/fail.
        pass

    def test_consistency(self, prompt: str, runs: int = 3) -> dict:
        """Test if a prompt produces consistent responses.

        Args:
            prompt: The prompt to send multiple times.
            runs: Number of times to run (default 3).

        Returns:
            A dict with:
                - prompt (str)
                - responses (list[str]): All responses
                - consistent (bool): True if all responses are identical
                - similarity_ratio (float): Fraction of responses that match the first one
        """
        # TODO: Implement this method.
        # 1. Call generate_fn(prompt) `runs` times, collect responses.
        # 2. Check if all are identical.
        # 3. Calculate similarity_ratio as matching / total.
        pass

    def test_format(self, prompt: str, expected_format: str = "json") -> dict:
        """Test if a prompt produces output in the expected format.

        Args:
            prompt: The prompt to send.
            expected_format: "json" or "markdown".

        Returns:
            A dict with:
                - passed (bool)
                - response (str)
                - format (str): The expected format
                - details (str): Description of the result
        """
        # TODO: Implement this method.
        # For "json": try json.loads(response), pass if no exception.
        # For "markdown": check if response contains "#" (a header).
        pass

    def run_test_suite(self, test_cases: list[dict]) -> dict:
        """Run a suite of test cases.

        Args:
            test_cases: List of dicts, each with:
                - name (str): Test case name
                - prompt (str): The prompt to test
                - checks (dict): Keyword args for test_prompt (expected_keywords, etc.)

        Returns:
            A dict with:
                - total (int): Number of test cases
                - passed (int): Number that passed
                - failed (int): Number that failed
                - results (list[dict]): Each result with {name, passed, details}
        """
        # TODO: Implement this method.
        # Loop through test_cases, run test_prompt for each, collect results.
        pass


def mock_llm(responses: list[str]):
    """Create a mock LLM function that cycles through predefined responses.

    Args:
        responses: List of response strings to return in order.
                   Cycles back to the start when exhausted.

    Returns:
        A callable that takes a prompt (str) and returns the next response.
    """
    # TODO: Implement this function.
    # Use a closure with a mutable index to track position.
    # Return responses[index % len(responses)] and increment index.
    pass


def evaluate_quality(
    response: str,
    reference: str,
    metrics: list[str] | None = None,
) -> dict:
    """Evaluate response quality against a reference answer.

    Args:
        response: The LLM's response.
        reference: The reference (ideal) answer.
        metrics: List of metrics to compute. Default: all.
            - "exact_match": True if response == reference
            - "keyword_overlap": Fraction of reference words found in response
            - "length_ratio": len(response) / len(reference), capped at 2.0

    Returns:
        A dict with the computed metrics.
    """
    # TODO: Implement this function.
    # 1. Default metrics to ["exact_match", "keyword_overlap", "length_ratio"].
    # 2. Compute each requested metric.
    # 3. Return the results dict.
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Create a mock LLM
    fake_llm = mock_llm([
        '{"answer": "Paris", "confidence": 0.95}',
        "The capital of France is Paris.",
        "# Paris\n\nParis is the capital of France.",
    ])

    harness = LLMTestHarness(fake_llm)

    print("=== Test Prompt ===")
    result = harness.test_prompt(
        "What is the capital of France?",
        expected_keywords=["Paris"],
        max_length=200,
    )
    print(json.dumps(result, indent=2))
    print()

    print("=== Test Format ===")
    fake_json = mock_llm(['{"key": "value"}'])
    json_harness = LLMTestHarness(fake_json)
    print(json.dumps(json_harness.test_format("Give me JSON", "json"), indent=2))
    print()

    print("=== Evaluate Quality ===")
    print(json.dumps(evaluate_quality(
        "Paris is the capital of France",
        "The capital of France is Paris",
    ), indent=2))
    print()

    print("=== Test Suite ===")
    suite_llm = mock_llm(["Paris is the capital of France."])
    suite_harness = LLMTestHarness(suite_llm)
    suite_result = suite_harness.run_test_suite([
        {"name": "basic_test", "prompt": "Capital of France?", "checks": {"expected_keywords": ["Paris"]}},
        {"name": "length_test", "prompt": "Capital of France?", "checks": {"max_length": 10}},
    ])
    print(json.dumps(suite_result, indent=2))
