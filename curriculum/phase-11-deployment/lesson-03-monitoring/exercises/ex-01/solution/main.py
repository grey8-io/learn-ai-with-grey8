"""
Exercise: Monitoring & Observability System — Solution
======================================================
"""

import json
import time
from collections import Counter
from datetime import datetime, timezone


class AIMetrics:
    """Collects and analyzes metrics for an AI application."""

    def __init__(self):
        """Initialize the metrics collector."""
        self.records = []

    def record_request(
        self,
        endpoint: str,
        latency_ms: float,
        tokens_in: int,
        tokens_out: int,
        status_code: int,
        model: str = "default",
    ) -> None:
        """Record a single request's metrics."""
        self.records.append({
            "endpoint": endpoint,
            "latency_ms": latency_ms,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "status_code": status_code,
            "model": model,
            "timestamp": time.time(),
        })

    def get_summary(self, time_window_minutes: int = 60) -> dict:
        """Get a summary of metrics within the given time window."""
        cutoff = time.time() - (time_window_minutes * 60)
        recent = [r for r in self.records if r["timestamp"] >= cutoff]

        if not recent:
            return {
                "total_requests": 0,
                "avg_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "error_rate": 0.0,
                "total_tokens": 0,
                "requests_per_minute": 0.0,
            }

        latencies = sorted([r["latency_ms"] for r in recent])
        total = len(recent)
        errors = sum(1 for r in recent if r["status_code"] >= 400)
        total_tokens = sum(r["tokens_in"] + r["tokens_out"] for r in recent)

        p95_index = min(int(total * 0.95), total - 1)

        return {
            "total_requests": total,
            "avg_latency_ms": round(sum(latencies) / total, 2),
            "p95_latency_ms": latencies[p95_index],
            "error_rate": round(errors / total, 4),
            "total_tokens": total_tokens,
            "requests_per_minute": round(total / time_window_minutes, 2),
        }

    def get_model_metrics(self, model: str) -> dict:
        """Get metrics for a specific model."""
        model_records = [r for r in self.records if r["model"] == model]

        if not model_records:
            return {
                "model": model,
                "total_requests": 0,
                "avg_latency_ms": 0.0,
                "total_tokens": 0,
                "error_rate": 0.0,
            }

        total = len(model_records)
        avg_latency = sum(r["latency_ms"] for r in model_records) / total
        total_tokens = sum(r["tokens_in"] + r["tokens_out"] for r in model_records)
        errors = sum(1 for r in model_records if r["status_code"] >= 400)

        return {
            "model": model,
            "total_requests": total,
            "avg_latency_ms": round(avg_latency, 2),
            "total_tokens": total_tokens,
            "error_rate": round(errors / total, 4),
        }

    def get_alerts(self, rules: list[dict]) -> list[dict]:
        """Check current metrics against alerting rules."""
        summary = self.get_summary()
        triggered = []

        for rule in rules:
            metric_value = summary.get(rule["metric"], 0)
            operator = rule["operator"]

            fired = False
            if operator == ">" and metric_value > rule["threshold"]:
                fired = True
            elif operator == "<" and metric_value < rule["threshold"]:
                fired = True

            if fired:
                triggered.append({
                    "metric": rule["metric"],
                    "operator": operator,
                    "threshold": rule["threshold"],
                    "value": metric_value,
                    "message": rule["message"],
                })

        return triggered


class StructuredLogger:
    """Produces JSON-formatted structured log lines."""

    def __init__(self, service_name: str):
        """Initialize the logger."""
        self.service_name = service_name

    def log(self, level: str, message: str, **context) -> str:
        """Create a structured log line."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            **context,
        }
        return json.dumps(entry)

    def log_request(self, method: str, path: str, status: int, latency_ms: float) -> str:
        """Log an HTTP request."""
        return self.log(
            "info",
            f"{method} {path} {status}",
            method=method,
            path=path,
            status=status,
            latency_ms=latency_ms,
        )

    def log_llm_call(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        success: bool,
    ) -> str:
        """Log an LLM API call."""
        level = "info" if success else "error"
        message = "LLM call completed" if success else "LLM call failed"
        return self.log(
            level,
            message,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            success=success,
        )


def create_dashboard_data(metrics: AIMetrics) -> dict:
    """Transform metrics into dashboard-ready data."""
    summary = metrics.get_summary()

    endpoint_counts = Counter(r["endpoint"] for r in metrics.records)
    top_endpoints = [
        {"endpoint": ep, "count": count}
        for ep, count in endpoint_counts.most_common(3)
    ]

    error_count = sum(1 for r in metrics.records if r["status_code"] >= 400)

    return {
        "requests_chart": {
            "total": summary["total_requests"],
            "error_count": error_count,
        },
        "latency_chart": {
            "avg_ms": summary["avg_latency_ms"],
            "p95_ms": summary["p95_latency_ms"],
        },
        "error_chart": {
            "error_rate": summary["error_rate"],
        },
        "top_endpoints": top_endpoints,
    }


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
