# Rubric — Caching & Batching

| Criterion | Points | Description |
|---|---|---|
| SemanticCache normalize_key works correctly | 15 | Lowercases, strips, removes punctuation, collapses whitespace |
| SemanticCache get/set with exact and normalized matching | 20 | Stores by normalized key, retrieves correctly, returns None on miss |
| SemanticCache tracks stats accurately | 10 | Hits, misses, hit_rate, and size are correct |
| SemanticCache evicts oldest on overflow | 10 | Removes first entry when at max_size |
| BatchProcessor processes in correct batch sizes | 15 | Respects batch_size, processes all items, handles empty queue |
| deduplicate_requests removes duplicates with correct mapping | 20 | Returns unique list and index_map, supports custom key_fn |
| Code quality | 10 | Clean classes, proper type hints, readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
