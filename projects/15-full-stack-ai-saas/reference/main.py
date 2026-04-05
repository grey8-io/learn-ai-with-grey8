"""
Project 15: Full-Stack AI SaaS (Reference)
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

# ChromaDB setup — in-memory vector store for the knowledge base
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="knowledge_base")

# FastAPI app with Jinja2 templates
app = FastAPI(title="AI SaaS App")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def chat(messages: list[dict]) -> str:
    """Send messages to Ollama and return the assistant's response."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "messages": messages, "stream": False},
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def add_to_knowledge_base(text: str, doc_id: str):
    """Split text into chunks and add them to the ChromaDB collection."""
    # Split into paragraphs, filtering out empty ones
    chunks = [p.strip() for p in text.split("\n\n") if p.strip()]

    # If paragraphs are too large, further split into ~500 char segments
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > 500:
            words = chunk.split()
            current = []
            current_len = 0
            for word in words:
                if current_len + len(word) > 500 and current:
                    final_chunks.append(" ".join(current))
                    current = []
                    current_len = 0
                current.append(word)
                current_len += len(word) + 1
            if current:
                final_chunks.append(" ".join(current))
        else:
            final_chunks.append(chunk)

    if not final_chunks:
        return

    # Add chunks to ChromaDB (it handles embedding automatically)
    collection.add(
        documents=final_chunks,
        ids=[f"{doc_id}_chunk_{i}" for i in range(len(final_chunks))],
    )


def search_knowledge_base(query: str, n_results: int = 3) -> list[str]:
    """Search the knowledge base for relevant document chunks."""
    # Check if collection has any documents
    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
    )
    return results["documents"][0] if results["documents"] else []


def chat_with_rag(user_message: str) -> str:
    """Answer a question using RAG — retrieval-augmented generation."""
    # Step 1: Retrieve relevant context from the knowledge base
    context_chunks = search_knowledge_base(user_message)

    # Step 2: Build the system prompt with context
    if context_chunks:
        context = "\n\n---\n\n".join(context_chunks)
        system_content = (
            "You are a helpful AI assistant with access to a knowledge base. "
            "Use the following context to answer the user's question. "
            "If the context doesn't contain relevant information, say so and "
            "answer to the best of your ability.\n\n"
            f"Context from knowledge base:\n{context}"
        )
    else:
        system_content = (
            "You are a helpful AI assistant. The knowledge base is currently empty. "
            "Answer the user's question to the best of your ability, and suggest "
            "they upload documents for more specific answers."
        )

    # Step 3: Generate response
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message},
    ]
    return chat(messages)


# --- Web Routes ---


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a text document to the knowledge base."""
    # Validate file type
    if not file.filename or not file.filename.endswith(".txt"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .txt files are supported."},
        )

    # Read and decode
    content = await file.read()
    text = content.decode("utf-8")

    if not text.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "File is empty."},
        )

    # Store in knowledge base
    add_to_knowledge_base(text, doc_id=file.filename)

    return {
        "message": f"Document '{file.filename}' uploaded successfully.",
        "chunks_stored": collection.count(),
        "characters": len(text),
    }


@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    """Chat with the AI using RAG."""
    try:
        response = chat_with_rag(message)
        return {"message": message, "response": response}
    except requests.RequestException as e:
        return JSONResponse(
            status_code=502,
            content={"error": f"Ollama API error: {str(e)}"},
        )


@app.get("/search")
async def search_endpoint(query: str):
    """Search the knowledge base directly."""
    results = search_knowledge_base(query, n_results=5)
    return {"query": query, "results": results, "count": len(results)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
