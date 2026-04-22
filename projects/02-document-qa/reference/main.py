"""
Project 02: Document QA — Reference Solution
==============================================
Ingest text/PDF files into ChromaDB and answer questions via RAG.
"""

import os
import requests
import chromadb
import PyPDF2

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"
CHUNK_SIZE = 500  # characters per chunk

# ---------------------------------------------------------------------------
# ChromaDB setup — in-memory for simplicity
# ---------------------------------------------------------------------------
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="documents")


def chat(prompt: str) -> str:
    """Send a single prompt to Ollama and return the response."""
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def read_file(filepath: str) -> str:
    """Read a .txt or .pdf file and return its text content."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        reader = PyPDF2.PdfReader(filepath)
        text = "".join(page.extract_text() or "" for page in reader.pages)
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into chunks of approximately `chunk_size` characters."""
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    return [c for c in chunks if c.strip()]


def ingest_document(filepath: str) -> int:
    """Read a file, chunk it, and add chunks to ChromaDB."""
    text = read_file(filepath)
    chunks = chunk_text(text)

    if not chunks:
        print(f"No content found in {filepath}")
        return 0

    # Build unique IDs for each chunk
    basename = os.path.basename(filepath)
    ids = [f"{basename}_chunk_{i}" for i in range(len(chunks))]

    # Add to ChromaDB (it handles embedding automatically)
    collection.add(documents=chunks, ids=ids)

    return len(chunks)


def query(question: str, n_results: int = 3) -> str:
    """Retrieve relevant chunks from ChromaDB and generate an answer."""
    # Check if collection has any documents
    if collection.count() == 0:
        return "No documents ingested yet. Please ingest a document first."

    # Retrieve the most relevant chunks
    results = collection.query(query_texts=[question], n_results=n_results)
    documents = results["documents"][0]

    # Build context from retrieved chunks
    context = "\n\n---\n\n".join(documents)

    # Build RAG prompt
    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer the question based only on the context above. "
        f"If the context does not contain enough information, say so."
    )

    return chat(prompt)


def main() -> None:
    """Interactive loop: ingest documents or ask questions."""
    print("=== Document QA System ===")
    print("Commands: enter a file path to ingest, 'ask' to query, 'quit' to exit\n")

    while True:
        try:
            user_input = input("Enter file path / 'ask' / 'quit': ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            if user_input.lower() == "ask":
                question = input("Question: ").strip()
                if question:
                    print(f"\nAnswer: {query(question)}\n")
                continue

            # Treat input as a file path
            if not os.path.isfile(user_input):
                print(f"File not found: {user_input}")
                continue

            count = ingest_document(user_input)
            print(f"Ingested {user_input} ({count} chunks)\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
