"""
Exercise: Document QA System
================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a complete document QA system with loading, chunking,
embedding, retrieval, and answer generation.
"""
import math
import os


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# TODO: Build a `DocumentQA` class with:
#
# __init__(self, embedding_fn, generate_fn)
#   - embedding_fn is a callable: embedding_fn(text) -> list[float]
#   - generate_fn is a callable: generate_fn(prompt) -> str
#   - Store both as instance attributes
#   - Initialize self.store as an empty list (will hold dicts with
#     "embedding", "text", "source" keys)
#
# load_documents(self, file_paths)
#   - Takes a list of file path strings
#   - Reads each file's text content
#   - Returns a list of dicts: [{"path": path, "content": text}, ...]
#   - Skip files that don't exist (use os.path.exists)
#
# process_documents(self, documents, chunk_size=500)
#   - Takes a list of document dicts (from load_documents)
#   - For each document, split content into chunks using simple
#     fixed-size chunking (no overlap needed):
#       chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
#   - For each chunk, compute its embedding using self.embedding_fn
#   - Append to self.store: {"embedding": emb, "text": chunk, "source": doc["path"]}
#   - Return the total number of chunks stored
#
# _retrieve(self, query, top_k=3)
#   - Embed the query using self.embedding_fn
#   - Compute cosine_similarity between query embedding and every
#     stored chunk's embedding
#   - Return the top_k chunks sorted by similarity (highest first)
#     as a list of dicts: [{"text": ..., "source": ..., "score": ...}, ...]
#
# answer(self, question, top_k=3)
#   - Retrieve the top_k chunks using self._retrieve
#   - Build context by joining chunk texts with "\n\n"
#   - Build prompt: "Based on the following context:\n{context}\n\nQuestion: {question}"
#   - Generate answer using self.generate_fn(prompt)
#   - Compute confidence as the average score of retrieved chunks
#   - Return dict: {"answer": ..., "sources": [list of source paths], "confidence": ...}
#
# evaluate_answer(self, answer, expected_keywords)
#   - Takes an answer string and a list of expected keyword strings
#   - Check how many expected_keywords appear in the answer (case-insensitive)
#   - Return dict: {"score": fraction_found, "found": [...], "missing": [...]}


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Simple mock functions for demonstration
    def mock_embed(text):
        # Fake embedding: just use character frequencies
        return [text.lower().count(c) / max(len(text), 1) for c in "abcdefghij"]

    def mock_generate(prompt):
        return "This is a generated answer based on the provided context."

    qa = DocumentQA(embedding_fn=mock_embed, generate_fn=mock_generate)

    # Create sample files for demo
    sample_dir = "__qa_demo__"
    os.makedirs(sample_dir, exist_ok=True)
    for i, content in enumerate(["Python is great.", "AI is the future.", "RAG is powerful."]):
        with open(os.path.join(sample_dir, f"doc{i}.txt"), "w") as f:
            f.write(content)

    files = [os.path.join(sample_dir, f"doc{i}.txt") for i in range(3)]
    docs = qa.load_documents(files)
    num_chunks = qa.process_documents(docs)
    print(f"Stored {num_chunks} chunks")

    result = qa.answer("What is Python?")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.2f}")

    # Cleanup
    import shutil
    shutil.rmtree(sample_dir)
