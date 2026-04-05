"""
Project 08: Streaming Chat App (Reference)

SSE streaming from Ollama via FastAPI with a simple HTML chat client.
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
    """Generator that streams tokens from Ollama."""
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Be concise and clear.",
                },
                {"role": "user", "content": user_message},
            ],
            "stream": True,
        },
        stream=True,  # Enable streaming on the requests side
    )
    response.raise_for_status()

    # Iterate over streamed lines from Ollama
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            token = data.get("message", {}).get("content", "")
            if token:
                yield {"data": token}
            if data.get("done", False):
                break


@app.post("/chat")
async def chat(req: ChatRequest):
    """SSE endpoint that streams chat responses token by token."""
    return EventSourceResponse(stream_chat(req.message))


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve a simple HTML chat interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streaming Chat</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: system-ui, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; }
        h1 { margin-bottom: 20px; color: #333; }
        #chat-box {
            border: 1px solid #ddd; border-radius: 8px; padding: 16px;
            height: 400px; overflow-y: auto; margin-bottom: 16px;
            background: #fafafa;
        }
        .msg { margin-bottom: 12px; line-height: 1.5; }
        .msg.user { color: #0066cc; }
        .msg.assistant { color: #333; }
        .msg strong { display: block; font-size: 0.85em; margin-bottom: 2px; }
        #input-row { display: flex; gap: 8px; }
        #user-input {
            flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 6px;
            font-size: 1em;
        }
        button {
            padding: 10px 20px; background: #0066cc; color: white; border: none;
            border-radius: 6px; cursor: pointer; font-size: 1em;
        }
        button:disabled { background: #999; }
    </style>
</head>
<body>
    <h1>Streaming Chat</h1>
    <div id="chat-box"></div>
    <div id="input-row">
        <input id="user-input" type="text" placeholder="Type a message..." autofocus />
        <button id="send-btn" onclick="sendMessage()">Send</button>
    </div>

    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');

        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            // Show user message
            appendMessage('user', message);
            userInput.value = '';
            sendBtn.disabled = true;

            // Create assistant message container
            const assistantDiv = appendMessage('assistant', '');

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message }),
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    // Parse SSE events from the buffer
                    const lines = buffer.split('\\n');
                    buffer = lines.pop(); // Keep incomplete line in buffer

                    for (const line of lines) {
                        if (line.startsWith('data:')) {
                            const token = line.slice(5).trim();
                            if (token) {
                                assistantDiv.querySelector('.content').textContent += token;
                                chatBox.scrollTop = chatBox.scrollHeight;
                            }
                        }
                    }
                }
            } catch (err) {
                assistantDiv.querySelector('.content').textContent += ' [Error: ' + err.message + ']';
            }

            sendBtn.disabled = false;
            userInput.focus();
        }

        function appendMessage(role, text) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.innerHTML = '<strong>' + role.toUpperCase() + '</strong><span class="content">' + escapeHtml(text) + '</span>';
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
            return div;
        }

        function escapeHtml(str) {
            const d = document.createElement('div');
            d.textContent = str;
            return d.innerHTML;
        }
    </script>
</body>
</html>
"""


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "model": MODEL}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
