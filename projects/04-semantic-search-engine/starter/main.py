"""
Project 04: Semantic Search Engine — Starter Code
===================================================
Embed documents into ChromaDB and search by meaning via a Flask REST API.

Your tasks:
  1. Implement add_document() to store text in ChromaDB
  2. Implement search() to find semantically similar documents
  3. Wire up the Flask routes
"""

import chromadb
import requests
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

# ---------------------------------------------------------------------------
# Flask app and ChromaDB setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="search_index")


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


def add_document(doc_id: str, text: str, metadata: dict | None = None) -> None:
    """
    Add a document to the ChromaDB collection.

    TODO:
    1. Call collection.add() with:
       - ids: [doc_id]
       - documents: [text]
       - metadatas: [metadata] if metadata is provided, otherwise omit
    2. ChromaDB will handle embedding automatically

    Hint: collection.add(ids=[doc_id], documents=[text])
    """
    pass  # <-- Replace with your implementation


def search(query_text: str, n_results: int = 5) -> list[dict]:
    """
    Search for documents similar to the query.

    TODO:
    1. Query ChromaDB: collection.query(query_texts=[query_text], n_results=n_results)
    2. The result has keys: "ids", "documents", "distances"
       - results["ids"][0] is a list of matched IDs
       - results["documents"][0] is a list of matched texts
       - results["distances"][0] is a list of distance scores
    3. Build and return a list of dicts:
       [{"id": ..., "text": ..., "distance": ...}, ...]
    """
    pass  # <-- Replace with your implementation


@app.route("/add", methods=["POST"])
def add_route():
    """
    POST /add — Add a document to the search index.

    Expected JSON body: {"id": "doc1", "text": "Some text...", "metadata": {...}}

    TODO:
    1. Parse the JSON body from the request
    2. Extract "id", "text", and optional "metadata"
    3. Validate that "id" and "text" are present
    4. Call add_document() with the extracted values
    5. Return a success JSON response
    """
    pass  # <-- Replace with your implementation


@app.route("/search", methods=["POST"])
def search_route():
    """
    POST /search — Search for similar documents.

    Expected JSON body: {"query": "search terms...", "n_results": 5}

    TODO:
    1. Parse the JSON body from the request
    2. Extract "query" and optional "n_results" (default 5)
    3. Validate that "query" is present
    4. Call search() and return the results as JSON
    """
    pass  # <-- Replace with your implementation


if __name__ == "__main__":
    print("Semantic Search Engine running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
