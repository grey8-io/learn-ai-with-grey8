"""
Exercise: RAG Pipeline
==============================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a Retrieval-Augmented Generation pipeline that wires together
a retriever and generator with context building and source tracking.
"""


# TODO: Build a `RAGPipeline` class with:
#
# __init__(self, retriever, generator)
#   - retriever is a callable: retriever(query, top_k) -> list[str]
#   - generator is a callable: generator(prompt) -> str
#   - Store both as instance attributes
#
# build_context(self, documents, max_chars=2000)
#   - Takes a list of document strings
#   - Concatenates them with "\n\n---\n\n" separator
#   - If the total length exceeds max_chars, truncate:
#     add documents one by one until adding the next would exceed the limit
#   - Return the concatenated context string
#
# build_prompt(self, query, context)
#   - Return a string in this exact format:
#     "Given the following context:\n{context}\n\nAnswer: {query}"
#
# query(self, question, top_k=3)
#   - Call self.retriever(question, top_k) to get documents
#   - Call self.build_context(documents) to build context
#   - Call self.build_prompt(question, context) to build the prompt
#   - Call self.generator(prompt) to get the answer
#   - Return the answer string
#
# query_with_sources(self, question, top_k=3)
#   - Call self.retriever(question, top_k) to get documents
#   - Call self.build_context(documents) to build context
#   - Call self.build_prompt(question, context) to build the prompt
#   - Call self.generator(prompt) to get the answer
#   - Return a dict: {"answer": answer, "sources": documents, "query": question}


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
