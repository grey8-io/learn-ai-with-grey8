# What Are Embeddings?

Up until now, you've used LLMs to generate text. But there's another incredibly powerful capability: turning text into **numbers**. These numbers -- called embeddings -- unlock similarity search, recommendation systems, clustering, and the entire world of RAG (Retrieval-Augmented Generation). In this lesson, you'll understand what embeddings are, why they matter, and how to work with them using basic math.

---

## From Words to Numbers

Computers don't understand text. They understand numbers. An **embedding** is a way to represent text (a word, sentence, or entire document) as a list of numbers -- a **vector**.

```python
# A simplified embedding (real ones have hundreds of dimensions)
"king"  -> [0.2, 0.8, 0.1, 0.9]
"queen" -> [0.3, 0.9, 0.1, 0.8]
"apple" -> [0.9, 0.1, 0.8, 0.2]
```

Notice that "king" and "queen" have similar numbers, while "apple" is very different. That's the magic -- **similar meanings produce similar vectors**.

---

## Vector Spaces (Intuitive)

Think of embeddings as coordinates on a map. Each word or sentence gets a position in a high-dimensional space. Words with similar meanings end up close together:

- "happy", "joyful", "cheerful" cluster together
- "sad", "depressed", "gloomy" cluster together
- These two clusters are far from each other

In a real embedding model, vectors have hundreds of dimensions (not just 2 or 3), so you can't visualize them directly. But the concept is the same: **distance in the vector space represents semantic similarity**.

```
  2D visualization (real embeddings have 100s of dimensions):

          happy • • joyful
                 •cheerful
     ↑
  meaning
     │
     │                   • apple
     │                • banana
     │
     │    sad •
     │         • depressed
     └──────────────────────→
                          meaning

  Similar words cluster together in vector space!
```

---

## Word Embeddings vs Sentence Embeddings

There are two main types:

**Word embeddings** represent individual words. Classic examples include Word2Vec and GloVe. They capture word-level meaning but miss context -- "bank" (river bank) and "bank" (financial bank) get the same vector.

**Sentence embeddings** represent entire sentences or paragraphs. Modern models like those in Ollama generate sentence-level embeddings that capture the full meaning of a text, including context. This is what you'll use in practice.

```python
# Sentence embeddings capture context
"I deposited money at the bank" -> [0.2, 0.8, ...]  # financial meaning
"I sat on the river bank"       -> [0.7, 0.3, ...]  # nature meaning
```

---

## Cosine Similarity

How do you measure if two vectors are similar? The most common method is **cosine similarity**. It measures the angle between two vectors, ignoring their length:

- **1.0** = identical direction (most similar)
- **0.0** = perpendicular (unrelated)
- **-1.0** = opposite direction (most dissimilar)

```
  Similarity = cos(angle between vectors)

       B →  /          A →  /
            /                /
           / θ small        / θ large
          /                /
    A →  /           B →  /

  cos(small θ) ≈ 0.95     cos(large θ) ≈ 0.20
  Very similar!            Not similar
```

The formula:

```
cosine_similarity(A, B) = (A . B) / (|A| * |B|)
```

Where:
- `A . B` is the dot product (sum of element-wise products)
- `|A|` is the magnitude (square root of sum of squares)

```python
import math

def cosine_similarity(vec_a, vec_b):
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
```

---

## Euclidean Distance

Another way to measure similarity is **Euclidean distance** -- the straight-line distance between two points:

```
distance(A, B) = sqrt(sum((a - b)^2 for a, b in zip(A, B)))
```

Unlike cosine similarity (where higher = more similar), with Euclidean distance **lower = more similar**. A distance of 0 means the vectors are identical.

```python
def euclidean_distance(vec_a, vec_b):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))
```

---

## Normalizing Vectors

A **normalized vector** (unit vector) has a length of 1. Normalizing is useful because:

1. It makes cosine similarity equal to the dot product (faster computation)
2. It removes the effect of vector magnitude, focusing only on direction
3. Many vector databases expect normalized vectors

```python
def normalize_vector(vec):
    magnitude = math.sqrt(sum(x * x for x in vec))
    if magnitude == 0:
        return vec
    return [x / magnitude for x in vec]
```

---

## How Ollama Generates Embeddings

Ollama's `/api/embeddings` endpoint turns text into vectors:

```python
import httpx

response = httpx.post(
    "http://localhost:11434/api/embeddings",
    json={"model": "tinyllama", "prompt": "Hello world"},
    timeout=30,
)
embedding = response.json()["embedding"]
# embedding is a list of floats, e.g., [0.023, -0.156, 0.891, ...]
```

The length of the vector depends on the model. TinyLlama produces 2048-dimensional vectors. Larger models may produce 4096 or more dimensions.

---

## Why Embeddings Matter for AI Apps

Embeddings are the foundation of:

- **Semantic search**: Find documents by meaning, not just keywords
- **RAG (Retrieval-Augmented Generation)**: Give LLMs access to your own documents
- **Recommendations**: "If you liked X, you'll like Y" (similar embeddings)
- **Clustering**: Group similar documents together automatically
- **Anomaly detection**: Find items that don't match the group

You'll build all of these in upcoming lessons. But first, you need to be comfortable with the math.

---

## Your Turn

In the exercise, you'll implement four fundamental vector operations: cosine similarity, Euclidean distance, finding the most similar vector, and normalizing vectors. No ML libraries needed -- just basic Python math. These operations are the building blocks for everything that comes next.

Let's do some vector math!
