# Rubric — RAG Pipeline

| Criterion | Points | Description |
|---|---|---|
| __init__ stores retriever and generator | 10 | Correctly stores both callables as instance attributes |
| build_context joins documents | 20 | Concatenates with separator, handles empty list |
| build_context respects max_chars | 15 | Stops adding documents when limit would be exceeded |
| build_prompt format | 15 | Returns exact expected format string |
| query runs full pipeline | 20 | Calls retrieve, build context, build prompt, generate in order |
| query_with_sources returns dict | 10 | Returns dict with answer, sources, and query keys |
| Code quality | 10 | Clean class with docstrings and type hints |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again — you've got this!
