"""
Project 08: Streaming Chat App (Starter)

SSE streaming from Ollama via FastAPI with a simple HTML chat client.

Setup (run once before this exercise):
    pip install requests sse-starlette

Your task: implement the streaming generator, SSE endpoint, and HTML client.
"""

import json
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import uvicorn

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

app = FastAPI(title="Streaming Chat App", version="1.0.0")


class ChatRequest(BaseModel):
    message: str


def stream_chat(user_message: str):
    """Generator that streams tokens from Ollama.

    Yields each token as it arrives from Ollama's streaming API.

    Args:
        user_message: The user's chat message.

    Yields:
        dict: Each yielded value should be {"data": token_text} for SSE.
    """
    # TODO: Send a POST request to OLLAMA_URL/api/chat with:
    #   - model: MODEL
    #   - messages: system message + user message
    #   - stream: True
    # IMPORTANT: Use requests.post(..., stream=True) to get a streaming response.
    #
    # TODO: Iterate over the response line by line:
    #   for line in response.iter_lines():
    #       - Decode each line as JSON
    #       - Extract the token from: data["message"]["content"]
    #       - Yield {"data": token} for the SSE stream
    #       - Stop when data.get("done") is True
    #
    # Hint: Each line from Ollama is a JSON object like:
    #   {"message": {"content": "Hello"}, "done": false}
    pass


@app.post("/chat")
async def chat(req: ChatRequest):
    """SSE endpoint that streams chat responses token by token."""
    # TODO: Return an EventSourceResponse that wraps stream_chat(req.message).
    # Hint: EventSourceResponse(stream_chat(req.message))
    pass


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve a simple HTML chat interface."""
    # TODO: Return an HTML string containing a chat interface with:
    #   - A message display area (div)
    #   - A text input and send button
    #   - JavaScript that:
    #     1. POSTs the message to /chat
    #     2. Reads the SSE stream using EventSource or fetch with ReadableStream
    #     3. Appends each token to the display area in real time
    #
    # Hint: Use fetch() with response.body.getReader() to read the stream,
    # or use the EventSource API for a simpler approach.
    pass


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "model": MODEL}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
