"""
Project 05: RAG Knowledge Base — Reference Solution
=====================================================
Ingest a folder of Markdown notes and answer questions using RAG.
"""

import os
from pathlib import Path
import httpx
import chromadb

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"
CHUNK_SIZE = 500  # characters per chunk

# ---------------------------------------------------------------------------
# ChromaDB setup
# ---------------------------------------------------------------------------
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="knowledge_base")


def chat(prompt: str) -> str:
    """Send a single prompt to Ollama and return the response."""
    response = httpx.post(
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


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into chunks of approximately `chunk_size` characters."""
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    return [c for c in chunks if c.strip()]


def ingest_folder(folder_path: str) -> tuple[int, int]:
    """Ingest all .md files from a folder into ChromaDB."""
    folder = Path(folder_path)
    md_files = sorted(folder.glob("**/*.md"))

    if not md_files:
        print(f"No .md files found in {folder_path}")
        return 0, 0

    total_files = 0
    total_chunks = 0

    for filepath in md_files:
        text = filepath.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        if not chunks:
            continue

        # Build unique IDs and metadata for each chunk
        filename = filepath.name
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in chunks]

        # Add to ChromaDB
        collection.add(documents=chunks, ids=ids, metadatas=metadatas)

        total_files += 1
        total_chunks += len(chunks)

    return total_files, total_chunks


def ask(question: str, n_results: int = 3) -> str:
    """Retrieve relevant chunks and generate an answer."""
    if collection.count() == 0:
        return "No documents ingested yet. Please ingest a folder first."

    # Clamp n_results to collection size
    n = min(n_results, collection.count())

    # Retrieve relevant chunks
    results = collection.query(query_texts=[question], n_results=n)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Build context with source attribution
    context_parts = []
    sources = set()
    for doc, meta in zip(documents, metadatas):
        context_parts.append(doc)
        sources.add(meta["source"])

    context = "\n\n---\n\n".join(context_parts)
    source_list = ", ".join(sorted(sources))

    # Build RAG prompt
    prompt = (
        f"Context (from: {source_list}):\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer the question based only on the context above. "
        f"If the context does not contain enough information, say so. "
        f"Mention which source files are relevant if possible."
    )

    return chat(prompt)


def main() -> None:
    """Interactive CLI: ingest a folder, then answer questions."""
    print("=== RAG Knowledge Base ===\n")

    # Step 1: Ingest a folder
    folder_path = input("Enter notes folder path: ").strip()

    if not folder_path or not Path(folder_path).is_dir():
        print(f"Invalid folder: {folder_path}")
        return

    print("Ingesting...")
    files, chunks = ingest_folder(folder_path)
    print(f"Ingested {files} file(s) ({chunks} chunks)\n")

    if chunks == 0:
        print("Nothing to query. Exiting.")
        return

    # Step 2: Question loop
    while True:
        try:
            question = input("Ask a question (or 'quit'): ").strip()

            if not question:
                continue

            if question.lower() == "quit":
                print("Goodbye!")
                break

            print("\nThinking...\n")
            answer = ask(question)
            print(f"Answer: {answer}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
