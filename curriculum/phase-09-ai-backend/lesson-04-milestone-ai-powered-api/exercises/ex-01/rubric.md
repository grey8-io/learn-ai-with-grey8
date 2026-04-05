# Rubric: AI-Powered API

| Criterion | Points |
|-----------|--------|
| `chat()` helper sends POST to Ollama and returns content string, with try/except raising `HTTPException(503)` on failure | 20 |
| Pydantic models correctly defined: `SummarizeRequest(text)`, `ClassifyRequest(text, categories)`, `GenerateRequest(prompt, max_tokens=200)`, `AIResponse(result)` | 20 |
| `/summarize` endpoint calls `chat()` with a summarization system prompt and returns `AIResponse` | 20 |
| `/classify` endpoint builds a system prompt including the provided categories and returns `AIResponse` | 20 |
| `/generate` endpoint calls `chat()` with a creative-writing system prompt and returns `AIResponse` | 20 |

**Total: 100 points**
