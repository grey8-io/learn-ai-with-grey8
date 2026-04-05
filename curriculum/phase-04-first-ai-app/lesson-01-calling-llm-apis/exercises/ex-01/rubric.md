# Rubric — OllamaChat Client

| Criterion | Points | Description |
|---|---|---|
| __init__ stores attributes | 15 | Correctly stores model and host with defaults |
| send() works without system prompt | 20 | Builds correct messages list and returns content |
| send() works with system prompt | 20 | Includes system message when provided |
| send_with_history() works | 25 | Passes full message history and returns content |
| Error handling (raise_for_status) | 10 | Calls raise_for_status on responses |
| Code quality | 10 | Clean class with docstrings and type hints |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again — you've got this!
