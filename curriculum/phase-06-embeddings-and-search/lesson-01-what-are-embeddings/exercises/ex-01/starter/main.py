"""
Exercise: Embedding Utilities
===============================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utility functions for working with embedding vectors.
No ML libraries needed -- just math!
"""
import math


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Cosine similarity measures the angle between two vectors:
    - 1.0 means identical direction (most similar)
    - 0.0 means perpendicular (unrelated)
    - -1.0 means opposite direction

    Formula: dot(A, B) / (magnitude(A) * magnitude(B))

    Args:
        vec_a: First vector as a list of floats.
        vec_b: Second vector as a list of floats.

    Returns:
        Cosine similarity as a float between -1.0 and 1.0.
        Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: Implement this function.
    # 1. Compute the dot product: sum(a * b for a, b in zip(vec_a, vec_b))
    # 2. Compute magnitude of vec_a: math.sqrt(sum(a * a for a in vec_a))
    # 3. Compute magnitude of vec_b: math.sqrt(sum(b * b for b in vec_b))
    # 4. If either magnitude is 0, return 0.0.
    # 5. Return dot_product / (mag_a * mag_b).
    pass


def euclidean_distance(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute Euclidean distance between two vectors.

    Lower distance = more similar. Distance of 0 = identical vectors.

    Formula: sqrt(sum((a - b)^2 for each dimension))

    Args:
        vec_a: First vector as a list of floats.
        vec_b: Second vector as a list of floats.

    Returns:
        Euclidean distance as a non-negative float.
    """
    # TODO: Implement this function.
    # Use math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))
    pass


def most_similar(query_vec: list[float], vectors: list[list[float]], labels: list[str]) -> str:
    """Find the most similar vector to the query and return its label.

    Uses cosine similarity to determine which vector in the collection
    is most similar to the query vector.

    Args:
        query_vec: The query vector to compare against.
        vectors: A list of vectors to search through.
        labels: A list of labels corresponding to each vector.

    Returns:
        The label of the most similar vector.
    """
    # TODO: Implement this function.
    # 1. Initialize best_score = -1 and best_index = 0.
    # 2. Loop through vectors with enumerate(vectors):
    #    - Compute cosine_similarity(query_vec, vec).
    #    - If the score is higher than best_score, update best_score and best_index.
    # 3. Return labels[best_index].
    pass


def normalize_vector(vec: list[float]) -> list[float]:
    """Normalize a vector to unit length (magnitude of 1).

    Args:
        vec: A vector as a list of floats.

    Returns:
        A new list representing the normalized vector.
        If the input vector has zero magnitude, returns it unchanged.
    """
    # TODO: Implement this function.
    # 1. Compute magnitude: math.sqrt(sum(x * x for x in vec))
    # 2. If magnitude is 0, return a copy of vec (or vec itself).
    # 3. Return [x / magnitude for x in vec].
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    a = [1.0, 0.0, 0.0]
    b = [0.0, 1.0, 0.0]
    c = [1.0, 0.0, 0.1]

    print(f"cosine_similarity(a, a) = {cosine_similarity(a, a)}")
    print(f"cosine_similarity(a, b) = {cosine_similarity(a, b)}")
    print(f"cosine_similarity(a, c) = {cosine_similarity(a, c):.4f}")
    print()

    print(f"euclidean_distance(a, a) = {euclidean_distance(a, a)}")
    print(f"euclidean_distance(a, b) = {euclidean_distance(a, b):.4f}")
    print()

    vectors = [[1, 0, 0], [0, 1, 0], [0.9, 0.1, 0]]
    labels = ["x-axis", "y-axis", "mostly-x"]
    query = [0.8, 0.2, 0]
    print(f"most_similar to {query}: {most_similar(query, vectors, labels)}")
    print()

    v = [3.0, 4.0]
    print(f"normalize_vector({v}) = {normalize_vector(v)}")
