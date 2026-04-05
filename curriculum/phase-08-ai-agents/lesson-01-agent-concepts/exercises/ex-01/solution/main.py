"""
Exercise: Simple Agent Framework — Solution
=============================================
"""
import re


class Tool:
    """A tool that an agent can use."""

    def __init__(self, name: str, description: str, function):
        """Initialize a tool.

        Args:
            name: The tool's name.
            description: What the tool does.
            function: The callable to execute.
        """
        self.name = name
        self.description = description
        self.function = function


class AgentState:
    """Tracks the state of an agent during execution."""

    def __init__(self):
        """Initialize agent state."""
        self.messages: list = []
        self.tool_results: list = []
        self.iteration: int = 0


class SimpleAgent:
    """A basic AI agent with tools and an action loop."""

    def __init__(self, tools: list, generate_fn, max_iterations: int = 5):
        """Initialize the agent.

        Args:
            tools: A list of Tool objects.
            generate_fn: A callable that takes a prompt string and returns a response string.
            max_iterations: Maximum number of tool-use iterations.
        """
        self.tools = tools
        self.generate_fn = generate_fn
        self.max_iterations = max_iterations

    def parse_action(self, response: str) -> dict | None:
        """Parse an LLM response for a tool action.

        Args:
            response: The LLM's response text.

        Returns:
            A dict with tool and args keys, or None if no action found.
        """
        match = re.search(r"ACTION:\s*(\w+)\((.+?)\)", response)
        if match:
            return {"tool": match.group(1), "args": match.group(2)}
        return None

    def execute_tool(self, tool_name: str, args: str) -> str:
        """Execute a tool by name with the given arguments.

        Args:
            tool_name: The name of the tool to execute.
            args: The argument string to pass to the tool.

        Returns:
            The tool's result as a string.
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return str(tool.function(args))
        return f"Error: Tool '{tool_name}' not found."

    def run(self, query: str) -> dict:
        """Run the agent loop until completion or max iterations.

        Args:
            query: The user's question or task.

        Returns:
            A dict with answer and iterations keys.
        """
        state = AgentState()
        state.messages.append({"role": "user", "content": query})

        for _ in range(self.max_iterations):
            prompt = "\n".join(m["content"] for m in state.messages)
            response = self.generate_fn(prompt)
            state.messages.append({"role": "assistant", "content": response})

            action = self.parse_action(response)
            if action is None:
                return {"answer": response, "iterations": state.iteration}

            result = self.execute_tool(action["tool"], action["args"])
            state.messages.append({"role": "tool", "content": result})
            state.tool_results.append(result)
            state.iteration += 1

        return {"answer": "Max iterations reached.", "iterations": state.iteration}


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Define some tools
    calc_tool = Tool(
        name="calculator",
        description="Evaluates a math expression",
        function=lambda expr: str(eval(expr)),
    )

    # Track call count for demo
    call_count = 0

    def mock_generate(prompt):
        global call_count
        call_count += 1
        if call_count == 1:
            return "I need to calculate this. ACTION: calculator(2 + 3)"
        return "The answer is 5."

    agent = SimpleAgent(
        tools=[calc_tool],
        generate_fn=mock_generate,
        max_iterations=5,
    )

    result = agent.run("What is 2 + 3?")
    print(f"Answer: {result['answer']}")
    print(f"Iterations: {result['iterations']}")
