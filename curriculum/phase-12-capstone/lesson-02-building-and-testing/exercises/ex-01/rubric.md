# Rubric — AI Testing Utilities

| Criterion | Points | Description |
|---|---|---|
| mock_llm cycles through responses correctly | 10 | Returns responses in order, cycles back to start |
| test_prompt checks expected/unexpected keywords | 20 | Case-insensitive keyword checking, correct pass/fail |
| test_prompt checks max_length | 10 | Fails when response exceeds limit |
| test_consistency measures response similarity | 15 | Runs multiple times, calculates similarity_ratio |
| test_format validates JSON and markdown | 15 | JSON parsing check, markdown header check |
| run_test_suite aggregates results correctly | 10 | Counts passed/failed, returns detailed results |
| evaluate_quality computes all metrics | 10 | exact_match, keyword_overlap, length_ratio |
| Code quality | 10 | Clean functions with type hints and readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
