# Rubric — Simple Vector Store

| Criterion | Points | Description |
|---|---|---|
| __init__ creates empty store | 10 | Initializes internal dict |
| add stores vectors and metadata | 20 | Correctly stores id, vector, and metadata (defaults to {}) |
| search returns ranked results | 25 | Computes cosine similarity, sorts descending, respects top_k |
| search result format | 10 | Each result has id, score, and metadata keys |
| delete removes documents | 15 | Removes by ID, handles non-existent IDs gracefully |
| count returns correct number | 10 | Reflects add/delete operations |
| Code quality | 10 | Clean class with docstrings and type hints |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
