"""
Exercise: Document QA System — Solution
==========================================
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


class DocumentQA:
    """A complete document QA system with retrieval and generation."""

    def __init__(self, embedding_fn, generate_fn):
        """Initialize the DocumentQA system.

        Args:
            embedding_fn: A callable that takes text and returns a list of floats.
            generate_fn: A callable that takes a prompt and returns a string.
        """
        self.embedding_fn = embedding_fn
        self.generate_fn = generate_fn
        self.store = []

    def load_documents(self, file_paths: list[str]) -> list[dict]:
        """Load text documents from file paths.

        Args:
            file_paths: A list of file path strings.

        Returns:
            A list of dicts with path and content keys.
        """
        documents = []
        for path in file_paths:
            if not os.path.exists(path):
                continue
            with open(path, "r") as f:
                documents.append({"path": path, "content": f.read()})
        return documents

    def process_documents(self, documents: list[dict], chunk_size: int = 500) -> int:
        """Chunk and embed documents, storing them in the vector store.

        Args:
            documents: A list of document dicts from load_documents.
            chunk_size: Maximum characters per chunk.

        Returns:
            The total number of chunks stored.
        """
        count = 0
        for doc in documents:
            content = doc["content"]
            chunks = [
                content[i : i + chunk_size]
                for i in range(0, len(content), chunk_size)
            ]
            for chunk in chunks:
                embedding = self.embedding_fn(chunk)
                self.store.append(
                    {
                        "embedding": embedding,
                        "text": chunk,
                        "source": doc["path"],
                    }
                )
                count += 1
        return count

    def _retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve the most relevant chunks for a query.

        Args:
            query: The user's question.
            top_k: Number of chunks to retrieve.

        Returns:
            A list of dicts with text, source, and score keys.
        """
        query_embedding = self.embedding_fn(query)
        scored = []
        for item in self.store:
            score = cosine_similarity(query_embedding, item["embedding"])
            scored.append(
                {
                    "text": item["text"],
                    "source": item["source"],
                    "score": score,
                }
            )
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def answer(self, question: str, top_k: int = 3) -> dict:
        """Answer a question using retrieved context.

        Args:
            question: The user's question.
            top_k: Number of chunks to retrieve.

        Returns:
            A dict with answer, sources, and confidence keys.
        """
        results = self._retrieve(question, top_k)
        context = "\n\n".join(r["text"] for r in results)
        prompt = f"Based on the following context:\n{context}\n\nQuestion: {question}"
        answer = self.generate_fn(prompt)
        confidence = (
            sum(r["score"] for r in results) / len(results) if results else 0.0
        )
        sources = [r["source"] for r in results]
        return {"answer": answer, "sources": sources, "confidence": confidence}

    def evaluate_answer(self, answer: str, expected_keywords: list[str]) -> dict:
        """Evaluate an answer against expected keywords.

        Args:
            answer: The generated answer string.
            expected_keywords: A list of keywords that should appear.

        Returns:
            A dict with score, found, and missing keys.
        """
        answer_lower = answer.lower()
        found = [kw for kw in expected_keywords if kw.lower() in answer_lower]
        missing = [kw for kw in expected_keywords if kw.lower() not in answer_lower]
        score = len(found) / len(expected_keywords) if expected_keywords else 0.0
        return {"score": score, "found": found, "missing": missing}


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
