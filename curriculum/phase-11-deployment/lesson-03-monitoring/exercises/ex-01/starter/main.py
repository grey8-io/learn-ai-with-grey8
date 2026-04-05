"""
Exercise: Monitoring & Observability System
============================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a monitoring system for AI applications.
"""

import json
import time


class AIMetrics:
    """Collects and analyzes metrics for an AI application."""

    def __init__(self):
        """Initialize the metrics collector.

        Should store a list of request records internally.
        """
        # TODO: Initialize an empty list to store request records.
        pass

    def record_request(
        self,
        endpoint: str,
        latency_ms: float,
        tokens_in: int,
        tokens_out: int,
        status_code: int,
        model: str = "default",
    ) -> None:
        """Record a single request's metrics.

        Args:
            endpoint: The API endpoint hit (e.g., "/chat").
            latency_ms: Response time in milliseconds.
            tokens_in: Number of input tokens.
            tokens_out: Number of output tokens.
            status_code: HTTP status code.
            model: Model name used for the request.

        Stores a dict with all fields plus a timestamp (time.time()).
        """
        # TODO: Append a dict with all fields and a timestamp to the records list.
        pass

    def get_summary(self, time_window_minutes: int = 60) -> dict:
        """Get a summary of metrics within the given time window.

        Args:
            time_window_minutes: Number of minutes to look back (default 60).

        Returns:
            A dict with:
                - total_requests (int)
                - avg_latency_ms (float, rounded to 2 decimals, 0.0 if no requests)
                - p95_latency_ms (float, the 95th percentile latency, 0.0 if no requests)
                - error_rate (float, fraction of requests with status >= 400, 0.0 if no requests)
                - total_tokens (int, sum of tokens_in + tokens_out)
                - requests_per_minute (float, total_requests / time_window_minutes, rounded to 2)
        """
        # TODO: Implement this method.
        # 1. Filter records within the time window.
        # 2. Calculate each metric.
        # 3. For p95: sort latencies, pick the value at index int(len * 0.95).
        # 4. Return the summary dict.
        pass

    def get_model_metrics(self, model: str) -> dict:
        """Get metrics for a specific model.

        Args:
            model: The model name to filter by.

        Returns:
            A dict with:
                - model (str)
                - total_requests (int)
                - avg_latency_ms (float, rounded to 2 decimals)
                - total_tokens (int)
                - error_rate (float)
        """
        # TODO: Implement this method.
        # Filter records by model name and compute metrics.
        pass

    def get_alerts(self, rules: list[dict]) -> list[dict]:
        """Check current metrics against alerting rules.

        Args:
            rules: List of dicts with:
                - metric (str): Key from get_summary() output
                - operator (str): ">" or "<"
                - threshold (float): Value to compare against
                - message (str): Alert message

        Returns:
            List of triggered alert dicts with {metric, operator, threshold, value, message}.
        """
        # TODO: Implement this method.
        # 1. Get current summary.
        # 2. For each rule, check if the metric crosses the threshold.
        # 3. Return list of triggered alerts.
        pass


class StructuredLogger:
    """Produces JSON-formatted structured log lines."""

    def __init__(self, service_name: str):
        """Initialize the logger.

        Args:
            service_name: Name of the service (included in every log line).
        """
        # TODO: Store service_name.
        pass

    def log(self, level: str, message: str, **context) -> str:
        """Create a structured log line.

        Args:
            level: Log level (e.g., "info", "error", "warning").
            message: Log message.
            **context: Additional key-value pairs to include.

        Returns:
            A JSON string with: timestamp, service, level, message, and any context fields.
        """
        # TODO: Implement this method.
        # Build a dict with timestamp (ISO format), service, level, message, and context.
        # Return json.dumps() of the dict.
        pass

    def log_request(self, method: str, path: str, status: int, latency_ms: float) -> str:
        """Log an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: Request path.
            status: HTTP status code.
            latency_ms: Response time in milliseconds.

        Returns:
            A structured log line (JSON string) for the request.
        """
        # TODO: Use self.log() with level="info" and appropriate message and context.
        pass

    def log_llm_call(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        success: bool,
    ) -> str:
        """Log an LLM API call.

        Args:
            model: Model name.
            prompt_tokens: Number of input tokens.
            completion_tokens: Number of output tokens.
            latency_ms: Call duration in milliseconds.
            success: Whether the call succeeded.

        Returns:
            A structured log line (JSON string) for the LLM call.
        """
        # TODO: Use self.log() with appropriate level and context.
        # level should be "info" if success else "error"
        pass


def create_dashboard_data(metrics: "AIMetrics") -> dict:
    """Transform metrics into dashboard-ready data.

    Args:
        metrics: An AIMetrics instance with recorded data.

    Returns:
        A dict with:
            - requests_chart (dict): {"total": int, "error_count": int}
            - latency_chart (dict): {"avg_ms": float, "p95_ms": float}
            - error_chart (dict): {"error_rate": float}
            - top_endpoints (list[dict]): Top 3 endpoints by request count,
              each as {"endpoint": str, "count": int}
    """
    # TODO: Implement this function.
    # 1. Get summary from metrics.
    # 2. Count requests per endpoint.
    # 3. Sort endpoints by count and take top 3.
    # 4. Return the dashboard dict.
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    metrics = AIMetrics()
    metrics.record_request("/chat", 1200, 150, 89, 200, "llama2")
    metrics.record_request("/chat", 800, 100, 50, 200, "llama2")
    metrics.record_request("/search", 300, 50, 20, 200, "llama2")
    metrics.record_request("/chat", 5000, 200, 150, 500, "llama2")

    print("=== Summary ===")
    print(json.dumps(metrics.get_summary(), indent=2))
    print()

    print("=== Model Metrics ===")
    print(json.dumps(metrics.get_model_metrics("llama2"), indent=2))
    print()

    alerts = metrics.get_alerts([
        {"metric": "error_rate", "operator": ">", "threshold": 0.1, "message": "High error rate!"},
        {"metric": "avg_latency_ms", "operator": ">", "threshold": 5000, "message": "Slow responses!"},
    ])
    print("=== Alerts ===")
    print(json.dumps(alerts, indent=2))
    print()

    logger = StructuredLogger("ai-api")
    print("=== Structured Logs ===")
    print(logger.log("info", "Server started", port=8000))
    print(logger.log_request("POST", "/chat", 200, 1200))
    print(logger.log_llm_call("llama2", 150, 89, 1200, True))
    print()

    print("=== Dashboard Data ===")
    print(json.dumps(create_dashboard_data(metrics), indent=2))
