"""
Project 05: RAG Knowledge Base — Starter Code
===============================================
Ingest a folder of Markdown notes and answer questions using RAG.

Setup (run once before this exercise):
    pip install chromadb

Your tasks:
  1. Implement ingest_folder() to read all .md files, chunk them, store in ChromaDB
  2. Implement ask() to retrieve relevant chunks and generate an answer
  3. Implement main() as an interactive CLI
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
    """
    Split text into chunks of approximately `chunk_size` characters.

    TODO:
    1. Split the text into chunks of `chunk_size` characters
    2. Return only non-empty chunks

    Hint: [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    """
    pass  # <-- Replace with your implementation


def ingest_folder(folder_path: str) -> tuple[int, int]:
    """
    Ingest all .md files from a folder into ChromaDB.

    TODO:
    1. Use Path(folder_path).glob("**/*.md") to find all Markdown files
    2. For each file:
       a. Read the file content
       b. Chunk it using chunk_text()
       c. Add chunks to ChromaDB with unique IDs (e.g., "filename_chunk_0")
       d. Include metadata: {"source": filename} for each chunk
    3. Return a tuple of (files_ingested, total_chunks)

    Hint for adding to ChromaDB with metadata:
      collection.add(
          documents=[chunk1, chunk2],
          ids=["id1", "id2"],
          metadatas=[{"source": "file.md"}, {"source": "file.md"}]
      )
    """
    pass  # <-- Replace with your implementation


def ask(question: str, n_results: int = 3) -> str:
    """
    Retrieve relevant chunks and generate an answer.

    TODO:
    1. Check if the collection has any documents (collection.count())
    2. Query ChromaDB for the top relevant chunks:
       results = collection.query(query_texts=[question], n_results=n_results)
    3. Extract the documents and their source metadata
    4. Build a RAG prompt:
       - Include the context chunks
       - Include the question
       - Instruct the LLM to answer based only on the provided context
       - Optionally mention which sources the context came from
    5. Call chat() and return the answer
    """
    pass  # <-- Replace with your implementation


def main() -> None:
    """
    Interactive CLI: ingest a folder, then answer questions.

    TODO:
    1. Ask the user for a folder path to ingest
    2. Call ingest_folder() and print how many files/chunks were ingested
    3. Loop:
       a. Ask the user for a question (or 'quit')
       b. If 'quit', break
       c. Call ask() and print the answer
    4. Handle errors gracefully
    """
    pass  # <-- Replace with your implementation


if __name__ == "__main__":
    main()
