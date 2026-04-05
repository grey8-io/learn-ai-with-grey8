"""
Exercise: Latency Optimization
=================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build performance monitoring and optimization tools.
"""

import time
import functools


class LatencyTracker:
    """Tracks operation latencies and computes statistics.

    Records start/end times for named operations and provides
    statistical summaries including percentiles.
    """

    def __init__(self):
        """Initialize the tracker.

        Attributes to set up:
            operations: dict mapping operation name -> list of durations (ms)
            pending: dict mapping operation name -> start timestamp
        """
        # TODO: Initialize self.operations = {} and self.pending = {}
        pass

    def start(self, operation_name: str) -> None:
        """Record the start time for an operation.

        Args:
            operation_name: Name of the operation being timed.
        """
        # TODO: Store time.time() in self.pending[operation_name]
        pass

    def end(self, operation_name: str) -> None:
        """Record the end time and compute duration for an operation.

        Calculates duration in milliseconds and appends to the
        operations list. Removes the pending entry.

        Does nothing if operation_name is not in pending.
        """
        # TODO:
        # 1. If operation_name not in self.pending, return.
        # 2. Calculate duration_ms = (time.time() - start) * 1000
        # 3. Append to self.operations[operation_name] (create list if needed).
        # 4. Delete from self.pending.
        pass

    def get_stats(self, operation_name: str = None) -> dict:
        """Get statistics for an operation or all operations.

        Args:
            operation_name: If provided, stats for that operation.
                           If None, stats across ALL recorded operations combined.

        Returns:
            Dict with keys: min, max, avg, p50, p95, p99, count.
            Returns empty dict if no data available.

        Percentile calculation:
            Sort the values, find the index at (len * percentile / 100),
            clamp to the last valid index.
        """
        # TODO:
        # 1. Collect durations: from the specific operation, or all operations combined.
        # 2. If no durations, return {}.
        # 3. Sort and compute min, max, avg.
        # 4. Compute p50, p95, p99 using: sorted_data[min(int(len*p/100), len-1)].
        # 5. Return the stats dict.
        pass

    def get_slow_operations(self, threshold_ms: float = 1000) -> list[dict]:
        """Find operations whose average duration exceeds the threshold.

        Args:
            threshold_ms: Threshold in milliseconds (default 1000).

        Returns:
            List of dicts with keys: operation, avg_ms, count.
            Sorted by avg_ms descending.
        """
        # TODO:
        # 1. For each operation, compute average duration.
        # 2. If average > threshold_ms, include it.
        # 3. Sort by avg_ms descending.
        pass


def measure(fn):
    """Decorator that records execution time of a function.

    Wraps fn and records the duration in milliseconds as an attribute
    `last_duration_ms` on the wrapper function.

    Usage:
        @measure
        def my_func():
            ...
        my_func()
        print(my_func.last_duration_ms)
    """
    # TODO:
    # 1. Use @functools.wraps(fn).
    # 2. In the wrapper, record start time, call fn, record end time.
    # 3. Set wrapper.last_duration_ms = (end - start) * 1000.
    # 4. Return the result.
    pass


class StreamBuffer:
    """Buffers small chunks for smoother streaming output.

    Accumulates text and only emits when the buffer reaches a minimum size.
    """

    def __init__(self, min_chars: int = 10):
        """Initialize the buffer.

        Args:
            min_chars: Minimum characters before emitting (default 10).
        """
        # TODO: Store min_chars and initialize self.buffer = ""
        pass

    def add(self, chunk: str) -> str:
        """Add a chunk to the buffer.

        If the buffer reaches min_chars, return the accumulated text
        and reset the buffer. Otherwise return empty string.

        Args:
            chunk: Text to add.

        Returns:
            Accumulated text if buffer >= min_chars, else "".
        """
        # TODO:
        # 1. Append chunk to self.buffer.
        # 2. If len(self.buffer) >= self.min_chars, save buffer, reset, return saved.
        # 3. Otherwise return "".
        pass

    def flush(self) -> str:
        """Return any remaining buffered content and reset.

        Returns:
            Whatever is left in the buffer (may be empty string).
        """
        # TODO: Save buffer content, reset to "", return saved.
        pass


def estimate_time(input_length: int, model_speed_tokens_per_sec: float = 30) -> float:
    """Estimate generation time in seconds.

    Assumes output length in tokens is approximately input_length // 4.

    Args:
        input_length: Length of input text in characters.
        model_speed_tokens_per_sec: Model's generation speed (default 30).

    Returns:
        Estimated time in seconds.
    """
    # TODO: output_tokens = input_length // 4; return output_tokens / model_speed_tokens_per_sec
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # LatencyTracker demo
    tracker = LatencyTracker()
    for i in range(5):
        tracker.start("inference")
        time.sleep(0.01 * (i + 1))
        tracker.end("inference")
    print("Stats:", tracker.get_stats("inference"))

    # Measure decorator demo
    @measure
    def slow_function():
        time.sleep(0.05)
        return "done"

    result = slow_function()
    print(f"\nMeasured: {slow_function.last_duration_ms:.1f}ms, result={result}")

    # StreamBuffer demo
    buffer = StreamBuffer(min_chars=5)
    for char in "Hello, World!":
        output = buffer.add(char)
        if output:
            print(f"Emitted: {output!r}")
    remaining = buffer.flush()
    if remaining:
        print(f"Flushed: {remaining!r}")

    # Estimate demo
    print(f"\nEstimated time for 1000 chars: {estimate_time(1000):.1f}s")
