# Rubric — Async AI Service Utilities

| Criterion | Points | Description |
|---|---|---|
| AsyncLLMClient init stores config correctly | 10 | base_url stripped of trailing slash, timeout stored |
| generate() makes async POST and returns response | 20 | Uses httpx.AsyncClient, posts to correct URL, extracts response |
| generate_stream() yields lines from streaming response | 15 | Uses client.stream and aiter_lines as async generator |
| batch_generate() processes concurrently with semaphore | 20 | Uses asyncio.Semaphore and asyncio.gather, returns ordered results |
| retry_with_backoff handles retries correctly | 20 | Exponential delays, raises on final failure, returns on success |
| create_sse_response formats chunks | 5 | Each chunk becomes "data: {chunk}\n\n" |
| Code quality | 10 | Clean async patterns, proper error handling, readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
