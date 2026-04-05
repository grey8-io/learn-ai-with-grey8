"""
Exercise: Caching & Batching — Solution
==========================================
"""

import re


class SemanticCache:
    """Cache with exact and normalized key matching."""

    def __init__(self, similarity_threshold: float = 0.9, max_size: int = 1000):
        self.similarity_threshold = similarity_threshold
        self.max_size = max_size
        self.store: dict[str, dict] = {}
        self.hits = 0
        self.misses = 0

    def normalize_key(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def get(self, query: str):
        normalized = self.normalize_key(query)
        if normalized in self.store:
            self.hits += 1
            return self.store[normalized]["response"]
        self.misses += 1
        return None

    def set(self, query: str, response, metadata=None) -> None:
        normalized = self.normalize_key(query)
        if len(self.store) >= self.max_size and normalized not in self.store:
            first_key = next(iter(self.store))
            del self.store[first_key]
        self.store[normalized] = {
            "query": query,
            "response": response,
            "metadata": metadata,
        }

    def get_stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total > 0 else 0.0,
            "size": len(self.store),
        }


class BatchProcessor:
    """Collects items and processes them in batches."""

    def __init__(self, process_fn, batch_size: int = 10, max_wait_seconds: float = 5.0):
        self.process_fn = process_fn
        self.batch_size = batch_size
        self.max_wait_seconds = max_wait_seconds
        self.queue: list = []

    def add(self, item) -> None:
        self.queue.append(item)

    def flush(self) -> list:
        results = []
        while self.queue:
            batch = self.queue[: self.batch_size]
            self.queue = self.queue[self.batch_size :]
            results.extend(self.process_fn(batch))
        return results

    def get_queue_size(self) -> int:
        return len(self.queue)


def deduplicate_requests(requests: list, key_fn=None) -> tuple[list, dict]:
    """Remove duplicate requests and create an index mapping."""
    if key_fn is None:
        key_fn = lambda x: x
    seen: dict = {}
    unique: list = []
    index_map: dict[int, int] = {}
    for i, req in enumerate(requests):
        key = key_fn(req)
        if key not in seen:
            seen[key] = len(unique)
            unique.append(req)
        index_map[i] = seen[key]
    return unique, index_map


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cache = SemanticCache(max_size=100)
    cache.set("What is Python?", "Python is a programming language.")
    print(f"Exact match: {cache.get('What is Python?')}")
    print(f"Normalized match: {cache.get('what is python')}")
    print(f"Miss: {cache.get('What is Java?')}")
    print(f"Stats: {cache.get_stats()}")

    processor = BatchProcessor(
        process_fn=lambda batch: [f"processed: {x}" for x in batch],
        batch_size=2,
    )
    for item in ["a", "b", "c", "d", "e"]:
        processor.add(item)
    print(f"\nQueue size: {processor.get_queue_size()}")
    results = processor.flush()
    print(f"Results: {results}")

    reqs = ["What is Python?", "Hello", "What is Python?", "World", "Hello"]
    unique, mapping = deduplicate_requests(reqs)
    print(f"\nOriginal: {reqs}")
    print(f"Unique: {unique}")
    print(f"Index map: {mapping}")
