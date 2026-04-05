# Rubric — Semantic Search Engine

| Criterion | Points | Description |
|---|---|---|
| __init__ stores embedding_fn and initializes store | 10 | Correctly stores the callable and empty dict |
| index_documents embeds and stores all documents | 15 | Calls embedding_fn for each doc, stores vector/text/metadata |
| search embeds query and ranks results | 20 | Computes cosine similarity, sorts descending, respects top_k |
| keyword_search scores by term frequency | 15 | Counts query term matches, normalizes by query length |
| hybrid_search combines both scores | 20 | Weights semantic by alpha and keyword by (1-alpha), sorts combined |
| Result format correctness | 10 | All methods return dicts with expected keys |
| Code quality | 10 | Clean class with docstrings, type hints, and readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
