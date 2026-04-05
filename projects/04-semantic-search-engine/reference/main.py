"""
Project 04: Semantic Search Engine — Reference Solution
========================================================
Embed documents into ChromaDB and search by meaning via a Flask REST API.
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
    """Add a document to the ChromaDB collection."""
    kwargs = {"ids": [doc_id], "documents": [text]}
    if metadata:
        kwargs["metadatas"] = [metadata]
    collection.add(**kwargs)


def search(query_text: str, n_results: int = 5) -> list[dict]:
    """Search for documents similar to the query text."""
    # Clamp n_results to actual collection size
    count = collection.count()
    if count == 0:
        return []
    n = min(n_results, count)

    results = collection.query(query_texts=[query_text], n_results=n)

    # Build a clean list of results
    output = []
    for i in range(len(results["ids"][0])):
        output.append(
            {
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    return output


@app.route("/add", methods=["POST"])
def add_route():
    """POST /add — Add a document to the search index."""
    data = request.get_json()

    if not data or "id" not in data or "text" not in data:
        return jsonify({"error": "Request must include 'id' and 'text'"}), 400

    add_document(
        doc_id=data["id"],
        text=data["text"],
        metadata=data.get("metadata"),
    )

    return jsonify({"status": "ok", "id": data["id"]}), 201


@app.route("/search", methods=["POST"])
def search_route():
    """POST /search — Search for similar documents."""
    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({"error": "Request must include 'query'"}), 400

    n_results = data.get("n_results", 5)
    results = search(data["query"], n_results=n_results)

    return jsonify({"results": results})


@app.route("/health", methods=["GET"])
def health():
    """GET /health — Check that the service is running."""
    return jsonify({"status": "ok", "documents": collection.count()})


if __name__ == "__main__":
    print("Semantic Search Engine running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
