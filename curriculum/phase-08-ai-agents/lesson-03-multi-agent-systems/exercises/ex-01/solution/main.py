"""
Exercise: Multi-Agent Orchestrator — Solution
================================================
"""


class AgentRole:
    """Defines an agent's role with name, prompt, and capabilities."""

    def __init__(self, name: str, system_prompt: str, capabilities: list[str]):
        """Initialize an agent role.

        Args:
            name: The agent's name.
            system_prompt: Instructions for this agent's behavior.
            capabilities: Keywords this agent can handle.
        """
        self.name = name
        self.system_prompt = system_prompt
        self.capabilities = capabilities


class Message:
    """A message passed between agents."""

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        message_type: str = "task",
    ):
        """Initialize a message.

        Args:
            from_agent: Name of the sending agent.
            to_agent: Name of the receiving agent.
            content: The message text.
            message_type: One of "task", "result", "feedback".
        """
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.content = content
        self.message_type = message_type


class Orchestrator:
    """Coordinates multiple agents to complete tasks."""

    def __init__(self, agents: dict, generate_fn):
        """Initialize the orchestrator.

        Args:
            agents: A dict mapping agent names to AgentRole objects.
            generate_fn: A callable that takes a prompt and returns a response.
        """
        self.agents = agents
        self.generate_fn = generate_fn
        self.messages: list = []

    def route_task(self, task: str) -> str | None:
        """Route a task to the most appropriate agent.

        Args:
            task: The task description.

        Returns:
            The name of the matching agent, or None if no match.
        """
        task_lower = task.lower()
        for name, agent in self.agents.items():
            for capability in agent.capabilities:
                if capability.lower() in task_lower:
                    return name
        return None

    def run_pipeline(self, task: str, pipeline: list[str]) -> str:
        """Run a sequential pipeline of agents.

        Args:
            task: The initial task description.
            pipeline: A list of agent names defining the execution order.

        Returns:
            The final output string.
        """
        current_input = task

        for i, agent_name in enumerate(pipeline):
            agent = self.agents[agent_name]
            prompt = f"{agent.system_prompt}\n\nInput: {current_input}"
            output = self.generate_fn(prompt)

            # Determine the next agent name for the message
            if i < len(pipeline) - 1:
                to_agent = pipeline[i + 1]
            else:
                to_agent = "output"

            msg = Message(
                from_agent=agent.name,
                to_agent=to_agent,
                content=output,
                message_type="result",
            )
            self.messages.append(msg)
            current_input = output

        return current_input

    def run_debate(
        self, question: str, agent_names: list[str], rounds: int = 2
    ) -> str:
        """Run a debate between agents over multiple rounds.

        Args:
            question: The question to debate.
            agent_names: Names of agents participating in the debate.
            rounds: Number of debate rounds.

        Returns:
            The last response string.
        """
        last_response = None

        for round_num in range(rounds):
            for i, agent_name in enumerate(agent_names):
                agent = self.agents[agent_name]

                if last_response is None:
                    prompt = f"{agent.system_prompt}\n\nQuestion: {question}"
                else:
                    prompt = (
                        f"{agent.system_prompt}\n\nQuestion: {question}"
                        f"\n\nPrevious response: {last_response}"
                    )

                output = self.generate_fn(prompt)

                # Determine the next agent in the rotation
                next_idx = (i + 1) % len(agent_names)
                to_agent = agent_names[next_idx]

                msg = Message(
                    from_agent=agent.name,
                    to_agent=to_agent,
                    content=output,
                    message_type="feedback",
                )
                self.messages.append(msg)
                last_response = output

        return last_response

    def collect_results(self) -> list[dict]:
        """Return all messages exchanged between agents.

        Returns:
            A list of message dicts.
        """
        return [
            {
                "from": msg.from_agent,
                "to": msg.to_agent,
                "content": msg.content,
                "type": msg.message_type,
            }
            for msg in self.messages
        ]


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
