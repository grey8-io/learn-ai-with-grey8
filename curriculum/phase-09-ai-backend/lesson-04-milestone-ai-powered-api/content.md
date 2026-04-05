# Milestone Project: AI-Powered API

Congratulations on completing Phase 9! You have learned how to build backend services with FastAPI, connect to a local LLM through Ollama, and structure your code with clean request/response models. Now it is time to put all of that together.

This is your **third milestone project**. You have come a long way since your first Python scripts and your second milestone building data pipelines. This time, you are building something that feels like a real product: a production-ready REST API that exposes AI capabilities through clean HTTP endpoints.

## What You'll Build

You will build a **FastAPI REST API** with three AI-powered endpoints:

- **POST /summarize** -- accepts text and returns a concise summary
- **POST /classify** -- accepts text and a list of categories, returns the best-matching category
- **POST /generate** -- accepts a creative prompt and returns generated text

Each endpoint sends a carefully crafted system prompt to Ollama's local LLM and returns the result as structured JSON. You will also implement a reusable `chat()` helper function and define Pydantic models for all request and response payloads.

### Architecture

```
                        +-----------------+
                        |     Client      |
                        | (curl / browser)|
                        +--------+--------+
                                 |
                          HTTP POST JSON
                                 |
                        +--------v--------+
                        |    FastAPI       |
                        |  /summarize     |
                        |  /classify      |
                        |  /generate      |
                        |  /health        |
                        +--------+--------+
                                 |
                         POST /api/chat
                                 |
                        +--------v--------+
                        |     Ollama      |
                        |  llama3.2:3b    |
                        +-----------------+
```

## Step-by-Step Guide

### Step 1: Implement the `chat()` Helper

The `chat()` function is the core of your API. It sends a request to Ollama and returns the LLM's response as a string. This is the single function that all three endpoints will call.

Use `requests.post()` to send a POST request to `OLLAMA_URL/api/chat`. The JSON payload needs three fields: `model` (the model name), `messages` (a list with a system message and a user message), and `stream` set to `False` so you get the complete response at once.

Wrap the entire call in a `try/except` block. If anything goes wrong -- the network is down, Ollama is not running, the model is not loaded -- raise an `HTTPException` with status code `503` (Service Unavailable) and a descriptive error message. This tells API consumers that the upstream LLM service is temporarily unavailable.

### Step 2: Define Pydantic Models

Create four Pydantic models that define the shape of your request and response data:

- **SummarizeRequest** -- a single `text: str` field containing the text to summarize
- **ClassifyRequest** -- a `text: str` field and a `categories: list[str]` field listing the allowed categories
- **GenerateRequest** -- a `prompt: str` field and an optional `max_tokens: int` field with a default of 200
- **AIResponse** -- a single `result: str` field containing the LLM's output

These models give you automatic request validation, clear API documentation, and type safety throughout your code.

### Step 3: Implement the Endpoints

Each endpoint follows the same pattern: receive a validated request, build a task-specific system prompt, call `chat()`, and return an `AIResponse`.

For `/summarize`, instruct the LLM to condense the user's text into a clear summary. For `/classify`, build a system prompt that lists the allowed categories and tells the LLM to respond with only the category name. For `/generate`, use a creative-writing system prompt that encourages clear, concise output.

The key insight is that the **system prompt is what makes each endpoint different**. The same `chat()` helper powers all three, but each endpoint's behavior is shaped by its unique instructions to the LLM.

### Step 4: Test with curl

Start your server and test each endpoint:

```bash
# Health check
curl http://localhost:8000/health

# Summarize
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Python is a versatile programming language used in web development, data science, artificial intelligence, and automation. It was created by Guido van Rossum and first released in 1991."}'

# Classify
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "The new GPU accelerates training by 3x", "categories": ["Technology", "Sports", "Cooking"]}'

# Generate
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a haiku about machine learning"}'
```

## Tips

- **Use descriptive system prompts.** The more specific your instructions to the LLM, the better the output. Tell it exactly what format you expect.
- **Test /health first.** If the health endpoint works but AI endpoints fail, the issue is with your Ollama connection or model configuration.
- **Check Swagger UI at /docs.** FastAPI automatically generates interactive API documentation. Open `http://localhost:8000/docs` in your browser to test endpoints without curl.
- **Pydantic does the validation.** You do not need to manually check if fields are missing -- FastAPI and Pydantic handle that automatically and return a 422 error with details.

## Your Turn

Open the starter file and implement all the TODO items. You have the `chat()` helper, four Pydantic models, and three endpoints to complete. Run the tests to verify your implementation, then try the curl commands above to see your AI-powered API in action. This is a real API pattern used in production -- you are building professional-grade software.
