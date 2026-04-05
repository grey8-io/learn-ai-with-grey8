# Rubric — Document Chunking Utilities

| Criterion | Points | Description |
|---|---|---|
| chunk_by_size works correctly | 20 | Splits text into fixed-size chunks with proper overlap |
| chunk_by_sentences works correctly | 20 | Groups sentences with overlap, handles edge cases |
| chunk_by_paragraphs works correctly | 20 | Splits on paragraphs, merges small ones, respects max size |
| chunk_markdown works correctly | 20 | Splits on headings, preserves structure |
| add_chunk_metadata works correctly | 10 | Returns correct metadata for each chunk |
| Code quality | 10 | Clean functions with docstrings and type hints |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again — you've got this!
