"""
Project 02: Document QA — Starter Code
========================================
Ingest text/PDF files into ChromaDB and answer questions via RAG.

Your tasks:
  1. Implement ingest_document() to read files, chunk text, and store in ChromaDB
  2. Implement query() to retrieve relevant chunks and generate an answer
  3. Implement the main() interactive loop
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
# ChromaDB setup
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
    """
    Read a file and return its text content.

    TODO:
    1. Check the file extension (use os.path.splitext)
    2. If it's a .pdf, use PyPDF2.PdfReader to extract text from all pages
    3. If it's a .txt (or other), read it as plain text
    4. Return the full text as a string

    Hint for PDF:
      reader = PyPDF2.PdfReader(filepath)
      text = "".join(page.extract_text() or "" for page in reader.pages)
    """
    pass  # <-- Replace with your implementation


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Split text into chunks of approximately `chunk_size` characters.

    TODO:
    1. Split the text into chunks of `chunk_size` characters
    2. Return a list of non-empty chunks

    Hint: A simple approach is slicing in a loop:
      [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    """
    pass  # <-- Replace with your implementation


def ingest_document(filepath: str) -> int:
    """
    Read a file, chunk it, and add chunks to ChromaDB.

    TODO:
    1. Call read_file() to get the text
    2. Call chunk_text() to split into chunks
    3. Add each chunk to the ChromaDB collection with:
       - documents: the chunk texts
       - ids: unique IDs like "filepath_chunk_0", "filepath_chunk_1", etc.
    4. Return the number of chunks ingested

    Hint: collection.add(documents=[...], ids=[...])
    """
    pass  # <-- Replace with your implementation


def query(question: str, n_results: int = 3) -> str:
    """
    Retrieve relevant chunks and generate an answer.

    TODO:
    1. Query ChromaDB for the top `n_results` relevant chunks:
       results = collection.query(query_texts=[question], n_results=n_results)
    2. Join the retrieved documents into a context string
    3. Build a prompt like:
       "Context:\n{context}\n\nQuestion: {question}\n\nAnswer based on the context above."
    4. Call chat() with the prompt and return the answer
    """
    pass  # <-- Replace with your implementation


def main() -> None:
    """
    Interactive loop: ingest documents or ask questions.

    TODO:
    1. Loop forever:
       a. Ask user for a file path to ingest, or 'ask' to query, or 'quit' to exit
       b. If 'quit', break
       c. If 'ask', prompt for a question and call query()
       d. Otherwise, treat input as a file path and call ingest_document()
    2. Handle errors gracefully (file not found, etc.)
    """
    pass  # <-- Replace with your implementation


if __name__ == "__main__":
    main()
