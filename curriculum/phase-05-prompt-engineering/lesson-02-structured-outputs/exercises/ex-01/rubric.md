# Rubric — Structured Output Parsers

| Criterion | Points | Description |
|---|---|---|
| extract_json handles clean and wrapped JSON | 20 | Finds JSON in text with surrounding content |
| extract_json handles missing/malformed JSON | 10 | Returns None gracefully for invalid input |
| extract_markdown_sections parses headings | 20 | Correctly splits markdown on heading markers |
| create_json_prompt assembles all parts | 15 | Includes task, schema, example, and JSON instruction |
| validate_llm_json checks required fields | 20 | Extracts JSON and identifies missing fields |
| validate_llm_json returns correct dict shape | 5 | Returns dict with valid, data, missing_fields keys |
| Code quality | 10 | Clean functions with error handling and type hints |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
