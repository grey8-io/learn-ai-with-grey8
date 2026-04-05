# Rubric — Talk to a Local AI

| Criterion | Points | Description |
|---|---|---|
| Function exists | 10 | `ask_ollama` is defined and callable |
| Correct URL | 15 | POSTs to `http://localhost:11434/api/generate` |
| Correct JSON body | 30 | Includes `model`, `prompt`, and `stream: false` |
| Timeout set | 15 | A timeout of at least 10 seconds is configured |
| Returns response text | 30 | Parses the JSON and returns the `"response"` string |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Re-read the "Talking to Ollama with Python" section in the lesson, paying attention to the httpx.post() call structure.
