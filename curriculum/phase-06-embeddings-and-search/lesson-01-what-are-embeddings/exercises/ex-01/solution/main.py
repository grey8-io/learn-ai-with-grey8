"""
Exercise: Embedding Utilities — Solution
==========================================
"""
import math


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        vec_a: First vector as a list of floats.
        vec_b: Second vector as a list of floats.

    Returns:
        Cosine similarity as a float between -1.0 and 1.0.
    """
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def euclidean_distance(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute Euclidean distance between two vectors.

    Args:
        vec_a: First vector as a list of floats.
        vec_b: Second vector as a list of floats.

    Returns:
        Euclidean distance as a non-negative float.
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))


def most_similar(query_vec: list[float], vectors: list[list[float]], labels: list[str]) -> str:
    """Find the most similar vector to the query and return its label.

    Args:
        query_vec: The query vector to compare against.
        vectors: A list of vectors to search through.
        labels: A list of labels corresponding to each vector.

    Returns:
        The label of the most similar vector.
    """
    best_index = 0
    best_score = -2.0  # cosine similarity minimum is -1

    for i, vec in enumerate(vectors):
        score = cosine_similarity(query_vec, vec)
        if score > best_score:
            best_score = score
            best_index = i

    return labels[best_index]


def normalize_vector(vec: list[float]) -> list[float]:
    """Normalize a vector to unit length.

    Args:
        vec: A vector as a list of floats.

    Returns:
        A new list representing the normalized vector.
    """
    magnitude = math.sqrt(sum(x * x for x in vec))
    if magnitude == 0:
        return list(vec)
    return [x / magnitude for x in vec]


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
