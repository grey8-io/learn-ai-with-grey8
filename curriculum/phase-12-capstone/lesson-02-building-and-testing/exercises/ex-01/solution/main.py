"""
Exercise: AI Testing Utilities — Solution
==========================================
"""

import json


class LLMTestHarness:
    """A test harness for evaluating LLM-powered functions."""

    def __init__(self, generate_fn):
        """Initialize the test harness."""
        self.generate_fn = generate_fn

    def test_prompt(
        self,
        prompt: str,
        expected_keywords: list[str] | None = None,
        unexpected_keywords: list[str] | None = None,
        max_length: int | None = None,
    ) -> dict:
        """Test a single prompt against criteria."""
        response = self.generate_fn(prompt)
        checks = []
        response_lower = response.lower()

        if expected_keywords:
            for keyword in expected_keywords:
                found = keyword.lower() in response_lower
                checks.append({
                    "check": f"contains '{keyword}'",
                    "passed": found,
                    "details": f"{'Found' if found else 'Not found'} in response",
                })

        if unexpected_keywords:
            for keyword in unexpected_keywords:
                absent = keyword.lower() not in response_lower
                checks.append({
                    "check": f"does not contain '{keyword}'",
                    "passed": absent,
                    "details": f"{'Not found' if absent else 'Found'} in response",
                })

        if max_length is not None:
            within_limit = len(response) <= max_length
            checks.append({
                "check": f"length <= {max_length}",
                "passed": within_limit,
                "details": f"Response length: {len(response)}",
            })

        all_passed = all(c["passed"] for c in checks) if checks else True

        return {
            "passed": all_passed,
            "response": response,
            "checks": checks,
        }

    def test_consistency(self, prompt: str, runs: int = 3) -> dict:
        """Test if a prompt produces consistent responses."""
        responses = [self.generate_fn(prompt) for _ in range(runs)]
        first = responses[0]
        matching = sum(1 for r in responses if r == first)

        return {
            "prompt": prompt,
            "responses": responses,
            "consistent": matching == len(responses),
            "similarity_ratio": round(matching / len(responses), 2),
        }

    def test_format(self, prompt: str, expected_format: str = "json") -> dict:
        """Test if a prompt produces output in the expected format."""
        response = self.generate_fn(prompt)

        if expected_format == "json":
            try:
                json.loads(response)
                return {
                    "passed": True,
                    "response": response,
                    "format": expected_format,
                    "details": "Valid JSON",
                }
            except (json.JSONDecodeError, TypeError):
                return {
                    "passed": False,
                    "response": response,
                    "format": expected_format,
                    "details": "Invalid JSON",
                }
        elif expected_format == "markdown":
            has_header = "#" in response
            return {
                "passed": has_header,
                "response": response,
                "format": expected_format,
                "details": "Contains markdown header" if has_header else "No markdown header found",
            }
        else:
            return {
                "passed": False,
                "response": response,
                "format": expected_format,
                "details": f"Unknown format: {expected_format}",
            }

    def run_test_suite(self, test_cases: list[dict]) -> dict:
        """Run a suite of test cases."""
        results = []
        passed_count = 0

        for case in test_cases:
            result = self.test_prompt(case["prompt"], **case.get("checks", {}))
            if result["passed"]:
                passed_count += 1
            results.append({
                "name": case["name"],
                "passed": result["passed"],
                "details": result["checks"],
            })

        return {
            "total": len(test_cases),
            "passed": passed_count,
            "failed": len(test_cases) - passed_count,
            "results": results,
        }


def mock_llm(responses: list[str]):
    """Create a mock LLM function that cycles through predefined responses."""
    index = [0]

    def generate(prompt: str) -> str:
        result = responses[index[0] % len(responses)]
        index[0] += 1
        return result

    return generate


def evaluate_quality(
    response: str,
    reference: str,
    metrics: list[str] | None = None,
) -> dict:
    """Evaluate response quality against a reference answer."""
    if metrics is None:
        metrics = ["exact_match", "keyword_overlap", "length_ratio"]

    results = {}

    if "exact_match" in metrics:
        results["exact_match"] = response == reference

    if "keyword_overlap" in metrics:
        ref_words = set(reference.lower().split())
        resp_words = set(response.lower().split())
        if ref_words:
            overlap = len(ref_words & resp_words) / len(ref_words)
        else:
            overlap = 1.0 if not resp_words else 0.0
        results["keyword_overlap"] = round(overlap, 2)

    if "length_ratio" in metrics:
        if len(reference) > 0:
            ratio = min(len(response) / len(reference), 2.0)
        else:
            ratio = 2.0 if len(response) > 0 else 1.0
        results["length_ratio"] = round(ratio, 2)

    return results


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
