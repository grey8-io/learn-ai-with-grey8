"""
Exercise: Semantic Search Engine
==================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a semantic search engine with hybrid search capability.
"""
import math
from typing import Callable


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class SemanticSearch:
    """A semantic search engine with hybrid search capability."""

    def __init__(self, embedding_fn: Callable[[str], list[float]]):
        """Initialize the search engine.

        Args:
            embedding_fn: A callable that takes a text string and returns
                          an embedding vector (list of floats).
        """
        # TODO: Store embedding_fn and initialize an internal store (dict).
        # self.embedding_fn = embedding_fn
        # self._store = {}
        pass

    def index_documents(self, documents: list[dict]) -> None:
        """Index a list of documents for searching.

        Each document is a dict with 'id', 'text', and optionally 'metadata'.
        This method embeds each document's text using self.embedding_fn
        and stores it internally.

        Args:
            documents: List of dicts with 'id', 'text', and optional 'metadata'.
        """
        # TODO: Implement this method.
        # For each document:
        # 1. Get the vector: self.embedding_fn(doc["text"])
        # 2. Store in self._store[doc["id"]] = {
        #        "vector": vector,
        #        "text": doc["text"],
        #        "metadata": doc.get("metadata", {}),
        #    }
        pass

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Perform semantic search.

        Embeds the query, computes cosine similarity against all indexed
        documents, and returns the top_k most similar.

        Args:
            query: The search query text.
            top_k: Number of results to return.

        Returns:
            A list of dicts with 'id', 'score', 'text', and 'metadata' keys,
            sorted by score (highest first).
        """
        # TODO: Implement this method.
        # 1. Embed the query: query_vector = self.embedding_fn(query)
        # 2. For each document in self._store, compute cosine_similarity.
        # 3. Build results list with id, score, text, metadata.
        # 4. Sort by score descending, return top_k.
        pass

    def keyword_search(self, query: str, documents: list[dict]) -> list[dict]:
        """Perform simple keyword-based search using term frequency.

        Scores each document by the fraction of query terms found in it.

        Args:
            query: The search query text.
            documents: List of dicts with 'id' and 'text' keys.

        Returns:
            A list of dicts with 'id', 'score', and 'text' keys,
            sorted by score (highest first).
        """
        # TODO: Implement this method.
        # 1. Split query into terms: query_terms = set(query.lower().split())
        # 2. For each document:
        #    a. Split doc["text"].lower() into words.
        #    b. Count how many query terms appear in the doc words.
        #    c. Score = matches / len(query_terms) if query_terms else 0.
        # 3. Sort by score descending.
        # 4. Return the scored list.
        pass

    def hybrid_search(self, query: str, documents: list[dict], alpha: float = 0.5) -> list[dict]:
        """Combine semantic and keyword search scores.

        Args:
            query: The search query text.
            documents: List of dicts with 'id' and 'text' keys
                       (needed for keyword search).
            alpha: Weight for semantic search (0.0 to 1.0).
                   1.0 = pure semantic, 0.0 = pure keyword.

        Returns:
            A list of dicts with 'id' and 'score' keys,
            sorted by combined score (highest first).
        """
        # TODO: Implement this method.
        # 1. Get semantic_results = self.search(query, top_k=len(self._store))
        # 2. Get keyword_results = self.keyword_search(query, documents)
        # 3. Build a combined scores dict:
        #    combined = {}
        #    For each semantic result: combined[id] = alpha * score
        #    For each keyword result: combined[id] = combined.get(id, 0) + (1 - alpha) * score
        # 4. Sort by combined score descending.
        # 5. Return list of {"id": id, "score": score}.
        pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Simple mock embedding: hash-based vector for demo purposes
    def mock_embedding(text: str) -> list[float]:
        """A simple mock embedding function."""
        words = text.lower().split()
        vec = [0.0] * 10
        for w in words:
            for i, ch in enumerate(w):
                vec[i % 10] += ord(ch) / 1000.0
        mag = math.sqrt(sum(x * x for x in vec))
        if mag > 0:
            vec = [x / mag for x in vec]
        return vec

    engine = SemanticSearch(mock_embedding)

    docs = [
        {"id": "d1", "text": "Python is a great programming language", "metadata": {"topic": "programming"}},
        {"id": "d2", "text": "Machine learning algorithms learn from data", "metadata": {"topic": "ml"}},
        {"id": "d3", "text": "Neural networks are used in deep learning", "metadata": {"topic": "dl"}},
    ]

    engine.index_documents(docs)

    print("Semantic search for 'programming with Python':")
    for r in engine.search("programming with Python", top_k=2):
        print(f"  {r['id']} (score: {r['score']:.3f}) - {r['text']}")

    print("\nKeyword search for 'learning':")
    for r in engine.keyword_search("learning", docs):
        print(f"  {r['id']} (score: {r['score']:.3f}) - {r['text']}")

    print("\nHybrid search for 'deep learning algorithms':")
    for r in engine.hybrid_search("deep learning algorithms", docs, alpha=0.5):
        print(f"  {r['id']} (score: {r['score']:.3f})")
