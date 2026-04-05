"""
Exercise: Multi-Agent Orchestrator
======================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a multi-agent orchestrator with routing, pipelines, and debates.
"""


# TODO: Build an `AgentRole` class with:
#   __init__(self, name, system_prompt, capabilities)
#     - name: str — the agent's name
#     - system_prompt: str — instructions for this agent's behavior
#     - capabilities: list[str] — keywords this agent can handle


# TODO: Build a `Message` class with:
#   __init__(self, from_agent, to_agent, content, message_type="task")
#     - from_agent: str — name of the sending agent
#     - to_agent: str — name of the receiving agent
#     - content: str — the message text
#     - message_type: str — one of "task", "result", "feedback"


# TODO: Build an `Orchestrator` class with:
#
# __init__(self, agents, generate_fn)
#   - agents: a dict of {name: AgentRole}
#   - generate_fn: callable that takes (str) -> str
#   - Store both as instance attributes
#   - Initialize self.messages as an empty list (will store Message objects)
#
# route_task(self, task)
#   - Determine which agent should handle the task
#   - For each agent, check if any of the agent's capabilities
#     appear as a substring in the task (case-insensitive)
#   - Return the name of the first agent that matches
#   - If no agent matches, return None
#
# run_pipeline(self, task, pipeline)
#   - pipeline is a list of agent names (strings) defining the order
#   - The first agent receives the task as input
#   - Each subsequent agent receives the previous agent's output as input
#   - For each agent in the pipeline:
#     * Build a prompt: "{agent.system_prompt}\n\nInput: {current_input}"
#     * Call self.generate_fn(prompt) to get output
#     * Create a Message(from_agent=agent.name, to_agent=next_agent_or "output",
#       content=output, message_type="result")
#     * Add the message to self.messages
#     * The output becomes the input for the next agent
#   - Return the final output string
#
# run_debate(self, question, agent_names, rounds=2)
#   - agent_names is a list of agent name strings (at least 2)
#   - For each round:
#     * Each agent in agent_names takes a turn
#     * First turn of first round: prompt is "{system_prompt}\n\nQuestion: {question}"
#     * All other turns: prompt is "{system_prompt}\n\nQuestion: {question}\n\nPrevious response: {last_response}"
#     * Call self.generate_fn(prompt)
#     * Create a Message and add to self.messages
#     * Track the last_response for the next agent
#   - Return the last response string
#
# collect_results(self)
#   - Return a list of dicts representing all messages:
#     [{"from": msg.from_agent, "to": msg.to_agent,
#       "content": msg.content, "type": msg.message_type}, ...]


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    planner = AgentRole(
        name="planner",
        system_prompt="You are a project planner. Break tasks into steps.",
        capabilities=["plan", "strategy", "organize"],
    )
    writer = AgentRole(
        name="writer",
        system_prompt="You are a technical writer. Write clear documentation.",
        capabilities=["write", "document", "explain"],
    )
    reviewer = AgentRole(
        name="reviewer",
        system_prompt="You are a code reviewer. Check for errors and improvements.",
        capabilities=["review", "check", "quality"],
    )

    call_count = 0

    def mock_generate(prompt):
        global call_count
        call_count += 1
        return f"[Response {call_count}] Based on the prompt, here is my output."

    agents = {"planner": planner, "writer": writer, "reviewer": reviewer}
    orch = Orchestrator(agents=agents, generate_fn=mock_generate)

    # Test routing
    routed = orch.route_task("Please review this code for bugs")
    print(f"Routed to: {routed}")

    # Test pipeline
    result = orch.run_pipeline("Write a guide about Python", ["planner", "writer", "reviewer"])
    print(f"Pipeline result: {result[:80]}...")

    # Test debate
    result = orch.run_debate("Is Python the best language?", ["writer", "reviewer"], rounds=2)
    print(f"Debate result: {result[:80]}...")

    print(f"\nTotal messages: {len(orch.collect_results())}")
