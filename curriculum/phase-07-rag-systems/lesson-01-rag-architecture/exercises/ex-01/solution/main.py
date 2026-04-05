"""
Exercise: RAG Pipeline — Solution
===================================
"""


class RAGPipeline:
    """A Retrieval-Augmented Generation pipeline."""

    def __init__(self, retriever, generator):
        """Initialize the RAG pipeline.

        Args:
            retriever: A callable that takes (query, top_k) and returns list[str].
            generator: A callable that takes (prompt) and returns str.
        """
        self.retriever = retriever
        self.generator = generator

    def build_context(self, documents: list[str], max_chars: int = 2000) -> str:
        """Concatenate retrieved documents into a context string.

        Args:
            documents: List of document strings.
            max_chars: Maximum character length for the context.

        Returns:
            A concatenated context string within the character limit.
        """
        separator = "\n\n---\n\n"
        parts = []
        current_length = 0

        for doc in documents:
            addition = len(doc)
            if parts:
                addition += len(separator)
            if current_length + addition > max_chars:
                break
            parts.append(doc)
            current_length += addition

        return separator.join(parts)

    def build_prompt(self, query: str, context: str) -> str:
        """Build an augmented prompt with context and query.

        Args:
            query: The user's question.
            context: The retrieved context string.

        Returns:
            A formatted prompt string.
        """
        return f"Given the following context:\n{context}\n\nAnswer: {query}"

    def query(self, question: str, top_k: int = 3) -> str:
        """Run the full RAG pipeline and return the answer.

        Args:
            question: The user's question.
            top_k: Number of documents to retrieve.

        Returns:
            The generated answer string.
        """
        documents = self.retriever(question, top_k)
        context = self.build_context(documents)
        prompt = self.build_prompt(question, context)
        answer = self.generator(prompt)
        return answer

    def query_with_sources(self, question: str, top_k: int = 3) -> dict:
        """Run the full RAG pipeline and return the answer with sources.

        Args:
            question: The user's question.
            top_k: Number of documents to retrieve.

        Returns:
            A dict with answer, sources, and query.
        """
        documents = self.retriever(question, top_k)
        context = self.build_context(documents)
        prompt = self.build_prompt(question, context)
        answer = self.generator(prompt)
        return {"answer": answer, "sources": documents, "query": question}


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Example with mock functions
    def mock_retriever(query, top_k=3):
        return [
            "Python was created by Guido van Rossum.",
            "Python 3.0 was released in 2008.",
            "Python is known for its readable syntax.",
        ][:top_k]

    def mock_generator(prompt):
        return "Python is a programming language created by Guido van Rossum."

    pipeline = RAGPipeline(retriever=mock_retriever, generator=mock_generator)
    result = pipeline.query_with_sources("What is Python?")
    print(f"Answer: {result['answer']}")
    print(f"Sources used: {len(result['sources'])}")
