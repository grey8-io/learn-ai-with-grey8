"""
Exercise: Token & Cost Management — Solution
===============================================
"""

import re


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text string."""
    return len(text) // 4


class CostTracker:
    """Tracks LLM usage and calculates costs."""

    def __init__(self, price_per_1k_input: float, price_per_1k_output: float):
        self.price_per_1k_input = price_per_1k_input
        self.price_per_1k_output = price_per_1k_output
        self.records: list[dict] = []

    def track(self, input_text: str, output_text: str, model: str = "default") -> None:
        input_tokens = estimate_tokens(input_text)
        output_tokens = estimate_tokens(output_text)
        cost = (
            input_tokens / 1000 * self.price_per_1k_input
            + output_tokens / 1000 * self.price_per_1k_output
        )
        self.records.append({
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "model": model,
        })

    def get_total_cost(self) -> float:
        return sum(r["cost"] for r in self.records)

    def get_usage_report(self) -> dict:
        total_requests = len(self.records)
        total_input_tokens = sum(r["input_tokens"] for r in self.records)
        total_output_tokens = sum(r["output_tokens"] for r in self.records)
        total_cost = self.get_total_cost()
        avg_cost = total_cost / total_requests if total_requests > 0 else 0.0
        return {
            "total_requests": total_requests,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_cost": total_cost,
            "avg_cost_per_request": avg_cost,
        }

    def get_model_breakdown(self) -> dict:
        breakdown: dict[str, dict] = {}
        for r in self.records:
            model = r["model"]
            if model not in breakdown:
                breakdown[model] = {
                    "requests": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0.0,
                }
            breakdown[model]["requests"] += 1
            breakdown[model]["input_tokens"] += r["input_tokens"]
            breakdown[model]["output_tokens"] += r["output_tokens"]
            breakdown[model]["cost"] += r["cost"]
        return breakdown


def optimize_prompt(prompt: str, max_tokens: int = 500) -> str:
    """Optimize a prompt to reduce token usage."""
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", prompt).strip()
    # Remove filler phrases
    fillers = [
        "I would like you to ",
        "Could you please ",
        "Please note that ",
        "It is important to note that ",
    ]
    for filler in fillers:
        cleaned = cleaned.replace(filler, "")
    cleaned = cleaned.strip()
    # Truncate to token budget
    max_chars = max_tokens * 4
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]
    return cleaned


def select_model(task_complexity: str, available_models: dict) -> str:
    """Select the best model for a given task complexity."""
    if task_complexity == "low":
        return max(available_models, key=lambda m: available_models[m]["speed"])
    elif task_complexity == "high":
        return max(available_models, key=lambda m: available_models[m]["quality"])
    else:
        return max(
            available_models,
            key=lambda m: available_models[m]["speed"] + available_models[m]["quality"],
        )


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tracker = CostTracker(price_per_1k_input=0.01, price_per_1k_output=0.03)
    tracker.track("What is Python?", "Python is a programming language.", "gpt-4")
    tracker.track("Summarize this.", "Here is the summary.", "gpt-3.5")
    print("Usage Report:", tracker.get_usage_report())
    print("Model Breakdown:", tracker.get_model_breakdown())

    verbose = "I would like you to   please summarize   the following text  "
    print(f"\nOriginal ({estimate_tokens(verbose)} tokens): {verbose!r}")
    optimized = optimize_prompt(verbose)
    print(f"Optimized ({estimate_tokens(optimized)} tokens): {optimized!r}")

    models = {
        "fast-model": {"context_window": 4096, "speed": 9, "quality": 5},
        "balanced": {"context_window": 8192, "speed": 6, "quality": 7},
        "smart-model": {"context_window": 32768, "speed": 3, "quality": 10},
    }
    print(f"\nLow complexity: {select_model('low', models)}")
    print(f"High complexity: {select_model('high', models)}")
    print(f"Medium complexity: {select_model('medium', models)}")
