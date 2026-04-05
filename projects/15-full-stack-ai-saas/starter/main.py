"""
Project 15: Full-Stack AI SaaS (Starter)
Complete mini-app: FastAPI backend with RAG + chat, Jinja2 HTML frontend.
"""

from pathlib import Path

import chromadb
import requests
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# Ollama API configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

# ChromaDB setup for the knowledge base
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="knowledge_base")

# FastAPI app with Jinja2 templates
app = FastAPI(title="AI SaaS App")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def chat(messages: list[dict]) -> str:
    """Send messages to Ollama and return the assistant's response.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.

    Returns:
        The assistant's response text.
    """
    # TODO: Send a POST request to OLLAMA_URL with:
    #   - "model": MODEL
    #   - "messages": messages
    #   - "stream": False
    # Return the assistant's message content.
    pass


def add_to_knowledge_base(text: str, doc_id: str):
    """Add a document to the ChromaDB knowledge base.

    Args:
        text: The document text to store.
        doc_id: A unique identifier for the document.
    """
    # TODO: Split the text into chunks (e.g., paragraphs or fixed-size chunks)
    # Hint: Split on double newlines, or every ~500 characters
    #
    # TODO: Add each chunk to the ChromaDB collection using:
    #   collection.add(
    #       documents=[chunk],
    #       ids=[f"{doc_id}_chunk_{i}"]
    #   )
    # ChromaDB handles embedding automatically.
    pass


def search_knowledge_base(query: str, n_results: int = 3) -> list[str]:
    """Search the knowledge base for relevant documents.

    Args:
        query: The search query.
        n_results: Number of results to return.

    Returns:
        A list of relevant document chunks.
    """
    # TODO: Query the ChromaDB collection:
    #   results = collection.query(query_texts=[query], n_results=n_results)
    #
    # TODO: Extract and return the document texts from the results
    # Hint: results["documents"][0] gives the list of matching texts
    #
    # TODO: Handle the case where the collection is empty
    pass


def chat_with_rag(user_message: str) -> str:
    """Answer a question using RAG — retrieval-augmented generation.

    Args:
        user_message: The user's question.

    Returns:
        The AI's response, informed by relevant documents.
    """
    # TODO: Step 1 — Search the knowledge base for relevant context
    # Call search_knowledge_base() with the user's message

    # TODO: Step 2 — Build a system prompt that includes the context
    # The system message should tell the LLM to:
    #   - Answer based on the provided context
    #   - If the context doesn't contain relevant info, say so
    #   - Include the retrieved documents in the system message

    # TODO: Step 3 — Call chat() with the system + user messages
    # Return the response
    pass


# --- Web Routes ---


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to the knowledge base.

    Accepts .txt files, reads their content, and stores in ChromaDB.
    """
    # TODO: Read the file content with `await file.read()`
    # TODO: Decode bytes to string
    # TODO: Validate it's a .txt file
    # TODO: Call add_to_knowledge_base() with the text and filename
    # TODO: Return JSON with a success message and document info
    pass


@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    """Chat with the AI using RAG.

    The AI will search the knowledge base for context before responding.
    """
    # TODO: Call chat_with_rag() with the user's message
    # TODO: Return JSON with the response
    pass


@app.get("/search")
async def search_endpoint(query: str):
    """Search the knowledge base directly.

    Args:
        query: Search query string.

    Returns:
        JSON with matching document chunks.
    """
    # TODO: Call search_knowledge_base() with the query
    # TODO: Return JSON with the results
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
