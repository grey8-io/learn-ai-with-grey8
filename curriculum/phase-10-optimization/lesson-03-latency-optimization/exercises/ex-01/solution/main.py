"""
Exercise: Latency Optimization — Solution
============================================
"""

import time
import functools


class LatencyTracker:
    """Tracks operation latencies and computes statistics."""

    def __init__(self):
        self.operations: dict[str, list[float]] = {}
        self.pending: dict[str, float] = {}

    def start(self, operation_name: str) -> None:
        self.pending[operation_name] = time.time()

    def end(self, operation_name: str) -> None:
        if operation_name not in self.pending:
            return
        duration_ms = (time.time() - self.pending[operation_name]) * 1000
        if operation_name not in self.operations:
            self.operations[operation_name] = []
        self.operations[operation_name].append(duration_ms)
        del self.pending[operation_name]

    def get_stats(self, operation_name: str = None) -> dict:
        if operation_name is not None:
            durations = self.operations.get(operation_name, [])
        else:
            durations = []
            for vals in self.operations.values():
                durations.extend(vals)

        if not durations:
            return {}

        sorted_d = sorted(durations)
        n = len(sorted_d)

        def _percentile(p):
            idx = min(int(n * p / 100), n - 1)
            return sorted_d[idx]

        return {
            "min": sorted_d[0],
            "max": sorted_d[-1],
            "avg": sum(sorted_d) / n,
            "p50": _percentile(50),
            "p95": _percentile(95),
            "p99": _percentile(99),
            "count": n,
        }

    def get_slow_operations(self, threshold_ms: float = 1000) -> list[dict]:
        slow = []
        for name, durations in self.operations.items():
            avg_ms = sum(durations) / len(durations)
            if avg_ms > threshold_ms:
                slow.append({
                    "operation": name,
                    "avg_ms": avg_ms,
                    "count": len(durations),
                })
        slow.sort(key=lambda x: x["avg_ms"], reverse=True)
        return slow


def measure(fn):
    """Decorator that records execution time of a function."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        wrapper.last_duration_ms = (end - start) * 1000
        return result

    wrapper.last_duration_ms = 0.0
    return wrapper


class StreamBuffer:
    """Buffers small chunks for smoother streaming output."""

    def __init__(self, min_chars: int = 10):
        self.min_chars = min_chars
        self.buffer = ""

    def add(self, chunk: str) -> str:
        self.buffer += chunk
        if len(self.buffer) >= self.min_chars:
            output = self.buffer
            self.buffer = ""
            return output
        return ""

    def flush(self) -> str:
        output = self.buffer
        self.buffer = ""
        return output


def estimate_time(input_length: int, model_speed_tokens_per_sec: float = 30) -> float:
    """Estimate generation time in seconds."""
    output_tokens = input_length // 4
    return output_tokens / model_speed_tokens_per_sec


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tracker = LatencyTracker()
    for i in range(5):
        tracker.start("inference")
        time.sleep(0.01 * (i + 1))
        tracker.end("inference")
    print("Stats:", tracker.get_stats("inference"))

    @measure
    def slow_function():
        time.sleep(0.05)
        return "done"

    result = slow_function()
    print(f"\nMeasured: {slow_function.last_duration_ms:.1f}ms, result={result}")

    buffer = StreamBuffer(min_chars=5)
    for char in "Hello, World!":
        output = buffer.add(char)
        if output:
            print(f"Emitted: {output!r}")
    remaining = buffer.flush()
    if remaining:
        print(f"Flushed: {remaining!r}")

    print(f"\nEstimated time for 1000 chars: {estimate_time(1000):.1f}s")
