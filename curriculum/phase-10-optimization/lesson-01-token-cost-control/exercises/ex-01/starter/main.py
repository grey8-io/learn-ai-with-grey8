"""
Exercise: Token & Cost Management
====================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utilities for tracking and optimizing AI costs.
"""

import re


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text string.

    Uses the rough approximation: 1 token ~ 4 characters.

    Args:
        text: Input text string.

    Returns:
        Estimated token count (integer).
    """
    # TODO: Return len(text) // 4
    pass


class CostTracker:
    """Tracks LLM usage and calculates costs.

    Attributes:
        price_per_1k_input: Cost per 1000 input tokens.
        price_per_1k_output: Cost per 1000 output tokens.
        records: List of usage records.
    """

    def __init__(self, price_per_1k_input: float, price_per_1k_output: float):
        """Initialize the cost tracker.

        Args:
            price_per_1k_input: Price per 1000 input tokens.
            price_per_1k_output: Price per 1000 output tokens.
        """
        # TODO: Store prices and initialize an empty records list.
        pass

    def track(self, input_text: str, output_text: str, model: str = "default") -> None:
        """Record a single LLM call.

        Uses estimate_tokens() to count tokens for input and output.
        Calculates cost as:
            (input_tokens / 1000 * price_per_1k_input) +
            (output_tokens / 1000 * price_per_1k_output)

        Appends a dict to self.records with keys:
            input_tokens, output_tokens, cost, model
        """
        # TODO: Estimate tokens, calculate cost, append record.
        pass

    def get_total_cost(self) -> float:
        """Return the total cost across all tracked calls."""
        # TODO: Sum up the "cost" field from all records.
        pass

    def get_usage_report(self) -> dict:
        """Generate a usage report.

        Returns:
            Dict with keys:
                total_requests (int): Number of tracked calls.
                total_input_tokens (int): Sum of all input tokens.
                total_output_tokens (int): Sum of all output tokens.
                total_cost (float): Sum of all costs.
                avg_cost_per_request (float): Average cost (0.0 if no requests).
        """
        # TODO: Aggregate all records into a report dict.
        pass

    def get_model_breakdown(self) -> dict:
        """Get cost breakdown per model.

        Returns:
            Dict mapping model name to dict with:
                requests (int), input_tokens (int), output_tokens (int), cost (float)
        """
        # TODO: Group records by model and sum up the stats.
        pass


def optimize_prompt(prompt: str, max_tokens: int = 500) -> str:
    """Optimize a prompt to reduce token usage.

    Steps:
        1. Replace multiple whitespace characters with a single space.
        2. Strip leading/trailing whitespace.
        3. Remove common filler phrases:
           - "I would like you to "
           - "Could you please "
           - "Please note that "
           - "It is important to note that "
        4. Truncate to max_tokens (max_tokens * 4 characters).

    Args:
        prompt: The original prompt text.
        max_tokens: Maximum token budget (default 500).

    Returns:
        Optimized prompt string.
    """
    # TODO: Implement the optimization steps above.
    pass


def select_model(task_complexity: str, available_models: dict) -> str:
    """Select the best model for a given task complexity.

    Args:
        task_complexity: One of "low", "medium", or "high".
        available_models: Dict mapping model name to a dict with keys:
            context_window (int), speed (int/float), quality (int/float).

    Returns:
        The name of the best model.

    Selection logic:
        - "low": Pick model with highest speed.
        - "high": Pick model with highest quality.
        - "medium" (or anything else): Pick model with highest (speed + quality).
    """
    # TODO: Implement model selection logic using max() with a key function.
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Cost tracking demo
    tracker = CostTracker(price_per_1k_input=0.01, price_per_1k_output=0.03)
    tracker.track("What is Python?", "Python is a programming language.", "gpt-4")
    tracker.track("Summarize this.", "Here is the summary.", "gpt-3.5")
    print("Usage Report:", tracker.get_usage_report())
    print("Model Breakdown:", tracker.get_model_breakdown())

    # Prompt optimization demo
    verbose = "I would like you to   please summarize   the following text  "
    print(f"\nOriginal ({estimate_tokens(verbose)} tokens): {verbose!r}")
    optimized = optimize_prompt(verbose)
    print(f"Optimized ({estimate_tokens(optimized)} tokens): {optimized!r}")

    # Model selection demo
    models = {
        "fast-model": {"context_window": 4096, "speed": 9, "quality": 5},
        "balanced": {"context_window": 8192, "speed": 6, "quality": 7},
        "smart-model": {"context_window": 32768, "speed": 3, "quality": 10},
    }
    print(f"\nLow complexity: {select_model('low', models)}")
    print(f"High complexity: {select_model('high', models)}")
    print(f"Medium complexity: {select_model('medium', models)}")
