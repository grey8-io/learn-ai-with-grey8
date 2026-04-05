# Rubric: Streaming Chat App

| Criterion | Points |
|-----------|--------|
| `stream_chat()` generator sends POST to Ollama with `stream=True`, iterates `iter_lines()`, and yields `{"data": token}` for each non-empty token | 30 |
| `/chat` SSE endpoint wraps `stream_chat()` in `EventSourceResponse` and returns streaming response with correct content type | 25 |
| `/` HTML page contains a chat display area, text input, and send button with proper structure | 25 |
| JavaScript in the HTML page uses `fetch()` with `ReadableStream` to read SSE events and append tokens to the UI in real time | 10 |
| Error handling: `stream_chat()` calls `raise_for_status()`, JavaScript catches fetch errors and displays them | 10 |

**Total: 100 points**
