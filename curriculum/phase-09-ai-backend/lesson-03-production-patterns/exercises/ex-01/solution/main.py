"""
Exercise: Production Patterns for AI Backends — Solution
==========================================================
"""

import hashlib
import time


class RateLimiter:
    """Sliding-window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}

    def _cleanup(self, client_id: str) -> None:
        now = time.time()
        if client_id in self.requests:
            self.requests[client_id] = [
                t for t in self.requests[client_id]
                if now - t < self.window_seconds
            ]

    def is_allowed(self, client_id: str) -> bool:
        if client_id not in self.requests:
            self.requests[client_id] = []
        self._cleanup(client_id)
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(time.time())
            return True
        return False

    def get_wait_time(self, client_id: str) -> float:
        if client_id not in self.requests:
            return 0.0
        self._cleanup(client_id)
        if len(self.requests[client_id]) < self.max_requests:
            return 0.0
        oldest = min(self.requests[client_id])
        wait = (oldest + self.window_seconds) - time.time()
        return max(wait, 0.0)


class ResponseCache:
    """TTL-based response cache for LLM outputs."""

    def __init__(self, max_size: int = 100, ttl_seconds: float = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: dict[str, dict] = {}

    def make_key(self, prompt: str, model: str) -> str:
        raw = f"{prompt}::{model}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, key: str):
        if key not in self.cache:
            return None
        entry = self.cache[key]
        if time.time() - entry["timestamp"] >= self.ttl_seconds:
            del self.cache[key]
            return None
        return entry["value"]

    def set(self, key: str, value) -> None:
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = min(self.cache, key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
        self.cache[key] = {"value": value, "timestamp": time.time()}

    def cleanup(self) -> None:
        now = time.time()
        expired = [
            k for k, v in self.cache.items()
            if now - v["timestamp"] >= self.ttl_seconds
        ]
        for k in expired:
            del self.cache[k]


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input for safe processing."""
    if not isinstance(text, str):
        return ""
    cleaned = "".join(
        ch for ch in text
        if ch in ("\n", "\t") or ord(ch) >= 32
    )
    cleaned = cleaned[:max_length]
    return cleaned.strip()


def create_error_response(error, status_code: int = 500) -> dict:
    """Create a standardized error response dictionary."""
    return {
        "error": {
            "message": str(error),
            "type": type(error).__name__,
            "status_code": status_code,
        }
    }


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    limiter = RateLimiter(max_requests=3, window_seconds=10)
    for i in range(5):
        print(f"Request {i+1}: allowed={limiter.is_allowed('user1')}")

    cache = ResponseCache(max_size=2, ttl_seconds=5)
    key = cache.make_key("Hello", "default")
    cache.set(key, "World")
    print(f"\nCache get: {cache.get(key)}")

    print(f"\nSanitized: '{sanitize_input('  Hello\x00World  ')}'")

    err = create_error_response(ValueError("bad input"), 400)
    print(f"\nError response: {err}")
