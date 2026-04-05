# Rubric — Fetch and Save JSON

| Criterion | Points | Description |
|---|---|---|
| fetch_and_save fetches correctly | 25 | Uses httpx.get with timeout, calls raise_for_status |
| fetch_and_save saves to file | 25 | Writes valid JSON with indent=2 |
| load_json reads correctly | 20 | Parses JSON file and returns dict |
| load_json handles missing file | 20 | Returns None for FileNotFoundError |
| Code quality | 10 | Clean code with docstrings and type hints |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again — you've got this!
