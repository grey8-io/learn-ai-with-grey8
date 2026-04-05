# Rubric — Multi-Agent Orchestrator

| Criterion | Points | Description |
|---|---|---|
| AgentRole stores attributes | 10 | Correctly stores name, system_prompt, capabilities |
| Message stores attributes with defaults | 10 | Stores all fields, message_type defaults to "task" |
| route_task matches capabilities | 15 | Case-insensitive keyword matching, returns None on no match |
| run_pipeline executes in order | 20 | Calls each agent in sequence, passes output as next input |
| run_debate runs multiple rounds | 20 | Each agent responds per round, builds on previous response |
| collect_results returns message log | 15 | Returns list of dicts with from, to, content, type keys |
| Code quality | 10 | Clean classes with docstrings and type hints |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again — you've got this!
