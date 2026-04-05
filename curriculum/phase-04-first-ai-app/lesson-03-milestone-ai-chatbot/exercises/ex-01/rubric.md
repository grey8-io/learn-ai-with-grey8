# Grading Rubric: AI Chatbot Milestone

| Criterion | Points |
|-----------|--------|
| `chat()` sends correct API request (POST to `/api/chat` with model, messages, stream=False) | 25 |
| `chat()` manages conversation history (appends user and assistant messages to history list) | 25 |
| `main()` implements input loop with `/quit` command to exit | 20 |
| Error handling (catches `ConnectionError` and `KeyboardInterrupt` gracefully) | 15 |
| Uses `rich` for formatted output (Markdown rendering, styled prompts, or panels) | 15 |

**Total: 100 points**

**Passing threshold: 70 points**

## Notes

- Partial credit is awarded for each criterion. For example, if `chat()` sends the request but does not manage history, award 25 out of 50 for those two criteria.
- The `/quit` command should be case-insensitive.
- Error handling should produce user-friendly messages, not raw tracebacks.
- Any use of `rich` (Console, Markdown, Panel, status spinner) counts for the formatting criterion.
