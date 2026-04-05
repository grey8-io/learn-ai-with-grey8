"""Tests for Exercise 1 — Latency Optimization."""

import importlib.util
import os
import time

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "solution", "main.py"
)


def _load_module(path: str):
    """Import main.py as a module from the given path."""
    spec = importlib.util.spec_from_file_location("student_main", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    return _load_module(SOLUTION_PATH)


# ---------------------------------------------------------------------------
# Tests — LatencyTracker
# ---------------------------------------------------------------------------

def test_tracker_records_duration(mod):
    """start/end should record a duration in milliseconds."""
    tracker = mod.LatencyTracker()
    tracker.start("op")
    time.sleep(0.05)  # 50ms
    tracker.end("op")
    stats = tracker.get_stats("op")
    assert stats["count"] == 1
    assert stats["min"] >= 40  # Allow some tolerance
    assert stats["max"] <= 200


def test_tracker_multiple_recordings(mod):
    """Multiple recordings should all be tracked."""
    tracker = mod.LatencyTracker()
    for _ in range(3):
        tracker.start("op")
        time.sleep(0.01)
        tracker.end("op")
    stats = tracker.get_stats("op")
    assert stats["count"] == 3
    assert stats["avg"] > 0


def test_tracker_percentiles(mod):
    """Stats should include p50, p95, p99."""
    tracker = mod.LatencyTracker()
    # Manually inject known durations to test percentiles
    tracker.operations["test"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    stats = tracker.get_stats("test")
    assert stats["min"] == 10
    assert stats["max"] == 100
    assert stats["avg"] == pytest.approx(55.0)
    assert stats["p50"] == 60  # index 5
    assert stats["count"] == 10


def test_tracker_empty_returns_empty_dict(mod):
    """get_stats for unknown operation should return empty dict."""
    tracker = mod.LatencyTracker()
    assert tracker.get_stats("nonexistent") == {}


def test_tracker_slow_operations(mod):
    """get_slow_operations should find operations above threshold."""
    tracker = mod.LatencyTracker()
    tracker.operations["fast_op"] = [10, 20, 30]
    tracker.operations["slow_op"] = [2000, 3000, 4000]
    tracker.operations["medium_op"] = [500, 600, 700]
    slow = tracker.get_slow_operations(threshold_ms=1000)
    assert len(slow) == 1
    assert slow[0]["operation"] == "slow_op"


def test_tracker_end_without_start(mod):
    """end() without start() should not raise."""
    tracker = mod.LatencyTracker()
    tracker.end("never_started")  # Should not raise
    assert tracker.get_stats("never_started") == {}


# ---------------------------------------------------------------------------
# Tests — measure decorator
# ---------------------------------------------------------------------------

def test_measure_records_time(mod):
    """measure decorator should set last_duration_ms on the wrapper."""
    @mod.measure
    def slow():
        time.sleep(0.05)
        return 42

    result = slow()
    assert result == 42
    assert slow.last_duration_ms >= 40
    assert slow.last_duration_ms <= 200


def test_measure_preserves_function_name(mod):
    """measure should preserve the wrapped function's name."""
    @mod.measure
    def my_function():
        pass

    assert my_function.__name__ == "my_function"


# ---------------------------------------------------------------------------
# Tests — StreamBuffer
# ---------------------------------------------------------------------------

def test_buffer_accumulates(mod):
    """Buffer should accumulate until min_chars is reached."""
    buffer = mod.StreamBuffer(min_chars=5)
    assert buffer.add("Hi") == ""
    assert buffer.add("!!") == ""
    result = buffer.add("X")  # Now 5 chars
    assert result == "Hi!!X"


def test_buffer_flush(mod):
    """flush should return remaining content."""
    buffer = mod.StreamBuffer(min_chars=10)
    buffer.add("Hello")
    assert buffer.flush() == "Hello"
    assert buffer.flush() == ""  # Already flushed


def test_buffer_emits_immediately_if_large_chunk(mod):
    """A chunk larger than min_chars should emit immediately."""
    buffer = mod.StreamBuffer(min_chars=3)
    result = buffer.add("Hello World")
    assert result == "Hello World"


# ---------------------------------------------------------------------------
# Tests — estimate_time
# ---------------------------------------------------------------------------

def test_estimate_time_basic(mod):
    """estimate_time should compute output_tokens / speed."""
    # 400 chars -> 100 tokens -> 100/30 = 3.33 seconds
    result = mod.estimate_time(400, model_speed_tokens_per_sec=30)
    assert result == pytest.approx(100 / 30)


def test_estimate_time_custom_speed(mod):
    """estimate_time should respect custom speed."""
    # 200 chars -> 50 tokens -> 50/50 = 1.0 second
    result = mod.estimate_time(200, model_speed_tokens_per_sec=50)
    assert result == pytest.approx(1.0)
