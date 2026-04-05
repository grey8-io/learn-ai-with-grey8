"""Tests for Exercise 1 — Caching & Batching."""

import importlib.util
import os

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
# Tests — SemanticCache
# ---------------------------------------------------------------------------

def test_cache_set_and_get_exact(mod):
    """Cache should return stored response for exact query."""
    cache = mod.SemanticCache(max_size=100)
    cache.set("What is Python?", "A programming language.")
    assert cache.get("What is Python?") == "A programming language."


def test_cache_normalized_match(mod):
    """Cache should match queries after normalization."""
    cache = mod.SemanticCache(max_size=100)
    cache.set("What is Python?", "A programming language.")
    assert cache.get("what is python") == "A programming language."
    assert cache.get("  WHAT  IS  PYTHON  ") == "A programming language."


def test_cache_miss_returns_none(mod):
    """Cache should return None for unknown queries."""
    cache = mod.SemanticCache(max_size=100)
    assert cache.get("unknown question") is None


def test_cache_stats_tracking(mod):
    """Cache should track hits and misses correctly."""
    cache = mod.SemanticCache(max_size=100)
    cache.set("hello", "world")
    cache.get("hello")  # hit
    cache.get("hello")  # hit
    cache.get("goodbye")  # miss
    stats = cache.get_stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["hit_rate"] == pytest.approx(2 / 3)
    assert stats["size"] == 1


def test_cache_eviction_at_max_size(mod):
    """Cache should evict oldest entry when at max_size."""
    cache = mod.SemanticCache(max_size=2)
    cache.set("query1", "response1")
    cache.set("query2", "response2")
    cache.set("query3", "response3")  # Should evict query1
    assert cache.get("query1") is None
    assert cache.get("query2") == "response2"
    assert cache.get("query3") == "response3"


def test_cache_normalize_removes_punctuation(mod):
    """normalize_key should remove punctuation."""
    cache = mod.SemanticCache()
    assert cache.normalize_key("What's up?") == "whats up"
    assert cache.normalize_key("hello...world!") == "helloworld"


# ---------------------------------------------------------------------------
# Tests — BatchProcessor
# ---------------------------------------------------------------------------

def test_batch_processor_processes_all_items(mod):
    """flush() should process all items and return results."""
    processor = mod.BatchProcessor(
        process_fn=lambda batch: [x * 2 for x in batch],
        batch_size=3,
    )
    for i in range(5):
        processor.add(i)
    results = processor.flush()
    assert results == [0, 2, 4, 6, 8]


def test_batch_processor_respects_batch_size(mod):
    """Items should be processed in chunks of batch_size."""
    batch_sizes_seen = []

    def track_batches(batch):
        batch_sizes_seen.append(len(batch))
        return batch

    processor = mod.BatchProcessor(process_fn=track_batches, batch_size=3)
    for i in range(7):
        processor.add(i)
    processor.flush()
    assert batch_sizes_seen == [3, 3, 1]


def test_batch_processor_queue_size(mod):
    """get_queue_size should reflect current queue state."""
    processor = mod.BatchProcessor(process_fn=lambda b: b, batch_size=5)
    assert processor.get_queue_size() == 0
    processor.add("item1")
    processor.add("item2")
    assert processor.get_queue_size() == 2
    processor.flush()
    assert processor.get_queue_size() == 0


def test_batch_processor_empty_flush(mod):
    """flush() with empty queue should return empty list."""
    processor = mod.BatchProcessor(process_fn=lambda b: b, batch_size=5)
    assert processor.flush() == []


# ---------------------------------------------------------------------------
# Tests — deduplicate_requests
# ---------------------------------------------------------------------------

def test_deduplicate_removes_duplicates(mod):
    """deduplicate should return unique items only."""
    reqs = ["a", "b", "a", "c", "b"]
    unique, index_map = mod.deduplicate_requests(reqs)
    assert unique == ["a", "b", "c"]


def test_deduplicate_index_map(mod):
    """index_map should map original indices to unique indices."""
    reqs = ["x", "y", "x", "z", "y"]
    unique, index_map = mod.deduplicate_requests(reqs)
    assert index_map[0] == 0  # "x" -> unique index 0
    assert index_map[1] == 1  # "y" -> unique index 1
    assert index_map[2] == 0  # "x" -> unique index 0
    assert index_map[3] == 2  # "z" -> unique index 2
    assert index_map[4] == 1  # "y" -> unique index 1


def test_deduplicate_with_key_fn(mod):
    """deduplicate should use key_fn when provided."""
    reqs = [{"q": "Hello"}, {"q": "hello"}, {"q": "World"}]
    unique, index_map = mod.deduplicate_requests(reqs, key_fn=lambda x: x["q"].lower())
    assert len(unique) == 2
    assert index_map[0] == index_map[1]  # "Hello" and "hello" map to same index
