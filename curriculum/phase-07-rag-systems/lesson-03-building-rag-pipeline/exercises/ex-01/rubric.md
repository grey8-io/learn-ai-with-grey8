# Rubric — Document QA System

| Criterion | Points | Description |
|---|---|---|
| __init__ stores functions and empty store | 10 | Correctly stores embedding_fn, generate_fn, initializes empty store |
| load_documents reads files | 15 | Reads files, returns correct dicts, skips missing files |
| process_documents chunks and embeds | 20 | Chunks content, embeds each chunk, stores in self.store |
| _retrieve finds similar chunks | 20 | Embeds query, computes cosine similarity, returns top-k |
| answer runs full pipeline | 20 | Retrieves, builds prompt, generates, returns dict with confidence |
| evaluate_answer checks keywords | 10 | Case-insensitive keyword matching with score |
| Code quality | 5 | Clean class with docstrings and type hints |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again — you've got this!
