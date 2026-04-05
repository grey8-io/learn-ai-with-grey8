# Grading Rubric: RAG Knowledge Base Milestone

| Criterion | Points |
|-----------|--------|
| `chunk_text()` correctly splits text into fixed-size chunks and filters empty ones | 15 |
| `ingest_folder()` reads all `.md` files from the folder recursively | 20 |
| `ingest_folder()` stores chunks in ChromaDB with unique IDs and source metadata | 20 |
| `ask()` retrieves relevant chunks from ChromaDB and builds a RAG prompt with context | 25 |
| `main()` implements interactive CLI with folder input and question loop | 10 |
| Error handling (empty collection check, missing folder, Ctrl+C, quit command) | 10 |

**Total: 100 points**

**Passing threshold: 70 points**

## Notes

- Partial credit is awarded for each criterion. For example, if `ingest_folder()` reads files but does not store metadata, award 20 out of 40 for those two criteria.
- The RAG prompt must include the retrieved context and the question. Bonus consideration for including source attribution.
- `chunk_text()` must filter out whitespace-only chunks to receive full credit.
- Chunk IDs must be unique across all files. The recommended pattern is `"filename_chunk_N"`.
