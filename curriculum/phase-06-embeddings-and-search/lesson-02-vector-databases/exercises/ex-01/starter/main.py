"""
Exercise: Simple Vector Store
================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build an in-memory vector store with cosine similarity search.
"""
import math


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class SimpleVectorStore:
    """A simple in-memory vector store with cosine similarity search."""

    def __init__(self):
        """Initialize an empty vector store.

        Use a dict to store documents:
            {id: {"vector": [...], "metadata": {...}}}
        """
        # TODO: Initialize self._store as an empty dict.
        pass

    def add(self, id: str, vector: list[float], metadata: dict | None = None) -> None:
        """Add a document to the store.

        Args:
            id: Unique identifier for the document.
            vector: The embedding vector.
            metadata: Optional metadata dict (default to empty dict if None).
        """
        # TODO: Store the vector and metadata in self._store under the given id.
        # If metadata is None, use an empty dict {}.
        pass

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """Search for the most similar vectors.

        Args:
            query_vector: The query embedding vector.
            top_k: Number of results to return.

        Returns:
            A list of dicts, each with 'id', 'score', and 'metadata' keys,
            sorted by score (highest first). Returns at most top_k results.
        """
        # TODO: Implement this method.
        # 1. For each document in self._store, compute cosine_similarity
        #    between query_vector and the stored vector.
        # 2. Build a list of {"id": id, "score": score, "metadata": metadata}.
        # 3. Sort by score descending (highest similarity first).
        # 4. Return the top_k results.
        pass

    def delete(self, id: str) -> None:
        """Remove a document from the store.

        Args:
            id: The ID of the document to remove.
                If the ID doesn't exist, do nothing.
        """
        # TODO: Remove the document with the given id from self._store.
        # Use dict.pop(id, None) to safely remove without error.
        pass

    def count(self) -> int:
        """Return the number of documents in the store.

        Returns:
            The number of documents currently stored.
        """
        # TODO: Return len(self._store).
        pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    store = SimpleVectorStore()

    store.add("doc1", [1.0, 0.0, 0.0], {"title": "About X"})
    store.add("doc2", [0.0, 1.0, 0.0], {"title": "About Y"})
    store.add("doc3", [0.9, 0.1, 0.0], {"title": "Mostly X"})
    print(f"Documents in store: {store.count()}")

    results = store.search([0.8, 0.2, 0.0], top_k=2)
    print("Top 2 results:")
    for r in results:
        print(f"  {r['id']} (score: {r['score']:.4f}) - {r['metadata']}")

    store.delete("doc2")
    print(f"After delete: {store.count()} documents")
