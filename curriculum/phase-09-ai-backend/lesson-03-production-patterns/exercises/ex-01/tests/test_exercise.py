"""Tests for Exercise 1 — Production Patterns for AI Backends."""

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
# Tests — RateLimiter
# ---------------------------------------------------------------------------

def test_rate_limiter_allows_under_limit(mod):
    """Requests under the limit should be allowed."""
    limiter = mod.RateLimiter(max_requests=3, window_seconds=10)
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True


def test_rate_limiter_blocks_over_limit(mod):
    """Requests over the limit should be blocked."""
    limiter = mod.RateLimiter(max_requests=2, window_seconds=10)
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is False


def test_rate_limiter_separate_clients(mod):
    """Different clients should have independent limits."""
    limiter = mod.RateLimiter(max_requests=1, window_seconds=10)
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user2") is True
    assert limiter.is_allowed("user1") is False


def test_rate_limiter_wait_time(mod):
    """get_wait_time should return 0 when under limit, positive when over."""
    limiter = mod.RateLimiter(max_requests=1, window_seconds=5.0)
    assert limiter.get_wait_time("user1") == 0.0
    limiter.is_allowed("user1")
    wait = limiter.get_wait_time("user1")
    assert wait > 0.0
    assert wait <= 5.0


# ---------------------------------------------------------------------------
# Tests — ResponseCache
# ---------------------------------------------------------------------------

def test_cache_set_and_get(mod):
    """Cache should store and retrieve values."""
    cache = mod.ResponseCache(max_size=10, ttl_seconds=60)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_miss(mod):
    """Cache should return None for missing keys."""
    cache = mod.ResponseCache(max_size=10, ttl_seconds=60)
    assert cache.get("nonexistent") is None


def test_cache_make_key_deterministic(mod):
    """make_key should return the same hash for the same inputs."""
    cache = mod.ResponseCache()
    key1 = cache.make_key("hello", "default")
    key2 = cache.make_key("hello", "default")
    key3 = cache.make_key("hello", "fast")
    assert key1 == key2
    assert key1 != key3


def test_cache_evicts_oldest_when_full(mod):
    """Cache should evict the oldest entry when at max_size."""
    cache = mod.ResponseCache(max_size=2, ttl_seconds=60)
    cache.set("key1", "val1")
    time.sleep(0.01)
    cache.set("key2", "val2")
    time.sleep(0.01)
    cache.set("key3", "val3")  # Should evict key1
    assert cache.get("key1") is None
    assert cache.get("key2") == "val2"
    assert cache.get("key3") == "val3"


def test_cache_cleanup_removes_expired(mod):
    """cleanup() should remove expired entries."""
    cache = mod.ResponseCache(max_size=10, ttl_seconds=0.05)
    cache.set("key1", "val1")
    time.sleep(0.1)
    cache.cleanup()
    assert cache.get("key1") is None


# ---------------------------------------------------------------------------
# Tests — sanitize_input
# ---------------------------------------------------------------------------

def test_sanitize_removes_control_chars(mod):
    """sanitize_input should remove control characters."""
    result = mod.sanitize_input("Hello\x00\x01\x02World")
    assert result == "HelloWorld"


def test_sanitize_keeps_newlines_and_tabs(mod):
    """sanitize_input should keep newlines and tabs."""
    result = mod.sanitize_input("Hello\n\tWorld")
    assert "Hello\n\tWorld" == result


def test_sanitize_enforces_max_length(mod):
    """sanitize_input should truncate to max_length."""
    result = mod.sanitize_input("a" * 200, max_length=50)
    assert len(result) == 50


def test_sanitize_non_string_returns_empty(mod):
    """sanitize_input should return empty string for non-string input."""
    assert mod.sanitize_input(123) == ""
    assert mod.sanitize_input(None) == ""


def test_sanitize_strips_whitespace(mod):
    """sanitize_input should strip leading and trailing whitespace."""
    result = mod.sanitize_input("  hello  ")
    assert result == "hello"


# ---------------------------------------------------------------------------
# Tests — create_error_response
# ---------------------------------------------------------------------------

def test_error_response_structure(mod):
    """create_error_response should return a properly structured dict."""
    err = mod.create_error_response(ValueError("bad input"), 400)
    assert "error" in err
    assert err["error"]["message"] == "bad input"
    assert err["error"]["type"] == "ValueError"
    assert err["error"]["status_code"] == 400


def test_error_response_default_status(mod):
    """create_error_response should default to status 500."""
    err = mod.create_error_response(RuntimeError("oops"))
    assert err["error"]["status_code"] == 500
