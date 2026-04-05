"""
Exercise: Semantic Search Engine — Solution
=============================================
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
            embedding_fn: A callable that takes text and returns a vector.
        """
        self.embedding_fn = embedding_fn
        self._store = {}

    def index_documents(self, documents: list[dict]) -> None:
        """Index a list of documents for searching.

        Args:
            documents: List of dicts with 'id', 'text', and optional 'metadata'.
        """
        for doc in documents:
            vector = self.embedding_fn(doc["text"])
            self._store[doc["id"]] = {
                "vector": vector,
                "text": doc["text"],
                "metadata": doc.get("metadata", {}),
            }

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Perform semantic search.

        Args:
            query: The search query text.
            top_k: Number of results to return.

        Returns:
            A list of dicts sorted by similarity score (highest first).
        """
        query_vector = self.embedding_fn(query)
        results = []
        for doc_id, doc in self._store.items():
            score = cosine_similarity(query_vector, doc["vector"])
            results.append({
                "id": doc_id,
                "score": score,
                "text": doc["text"],
                "metadata": doc["metadata"],
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def keyword_search(self, query: str, documents: list[dict]) -> list[dict]:
        """Perform simple keyword-based search using term frequency.

        Args:
            query: The search query text.
            documents: List of dicts with 'id' and 'text' keys.

        Returns:
            A list of dicts sorted by keyword match score (highest first).
        """
        query_terms = set(query.lower().split())
        results = []
        for doc in documents:
            doc_words = doc["text"].lower().split()
            matches = sum(1 for term in query_terms if term in doc_words)
            score = matches / len(query_terms) if query_terms else 0
            results.append({
                "id": doc["id"],
                "score": score,
                "text": doc["text"],
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def hybrid_search(self, query: str, documents: list[dict], alpha: float = 0.5) -> list[dict]:
        """Combine semantic and keyword search scores.

        Args:
            query: The search query text.
            documents: List of dicts with 'id' and 'text' keys.
            alpha: Weight for semantic search (1.0 = pure semantic, 0.0 = pure keyword).

        Returns:
            A list of dicts sorted by combined score (highest first).
        """
        semantic_results = self.search(query, top_k=len(self._store))
        keyword_results = self.keyword_search(query, documents)

        combined = {}
        for r in semantic_results:
            combined[r["id"]] = alpha * r["score"]
        for r in keyword_results:
            combined[r["id"]] = combined.get(r["id"], 0) + (1 - alpha) * r["score"]

        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        return [{"id": doc_id, "score": score} for doc_id, score in ranked]


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
