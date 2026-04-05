# Rubric — Simple Agent Framework

| Criterion | Points | Description |
|---|---|---|
| Tool class stores attributes | 10 | Correctly stores name, description, and function |
| AgentState initializes correctly | 10 | Empty messages/tool_results lists and iteration=0 |
| parse_action extracts actions | 20 | Regex parses ACTION: tool(args) pattern, returns None when absent |
| execute_tool finds and calls tools | 15 | Matches by name, calls function, handles missing tools |
| run completes without tools | 20 | Returns direct answer when no action parsed |
| run executes tool loop | 15 | Calls tools, feeds results back, respects max_iterations |
| Code quality | 10 | Clean classes with docstrings and type hints |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again — you've got this!
