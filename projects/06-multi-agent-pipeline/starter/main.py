"""
Project 06: Multi-Agent Pipeline (Starter)

Chain specialized AI agents to research, write, and review content.
Each agent is an LLM call with a focused system prompt.

Your task: implement the Agent class and pipeline logic.
"""

import sys
import requests

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"


def chat(system_prompt: str, user_message: str) -> str:
    """Send a chat request to Ollama and return the assistant's response.

    Args:
        system_prompt: The system message that defines the agent's role.
        user_message: The user message (input for this agent).

    Returns:
        The assistant's response text.
    """
    # TODO: Send a POST request to OLLAMA_URL/api/chat with:
    #   - model: MODEL
    #   - messages: a list with system and user messages
    #   - stream: False
    # Return the assistant's response content from the JSON response.
    # Hint: response.json()["message"]["content"]
    pass


class Agent:
    """A specialized AI agent with a name and system prompt."""

    def __init__(self, name: str, system_prompt: str):
        """Initialize the agent.

        Args:
            name: Human-readable name (e.g., "Researcher").
            system_prompt: Instructions that define this agent's behavior.
        """
        # TODO: Store the name and system_prompt as instance attributes.
        pass

    def run(self, input_text: str) -> str:
        """Run this agent on the given input.

        Args:
            input_text: The text input for this agent to process.

        Returns:
            The agent's output text.
        """
        # TODO: Print which agent is running (e.g., "[Researcher] Working...")
        # TODO: Call the chat() helper with this agent's system_prompt and input_text.
        # TODO: Return the result.
        pass


def create_agents() -> list:
    """Create the three pipeline agents: Researcher, Writer, Reviewer.

    Returns:
        A list of Agent objects in pipeline order.
    """
    # TODO: Create a Researcher agent whose system prompt instructs it to:
    #   - Act as a research analyst
    #   - Gather key facts, statistics, and perspectives on the given topic
    #   - Output a structured research brief

    # TODO: Create a Writer agent whose system prompt instructs it to:
    #   - Act as a skilled article writer
    #   - Take research notes and write a well-structured article
    #   - Include an introduction, body sections, and conclusion

    # TODO: Create a Reviewer agent whose system prompt instructs it to:
    #   - Act as an editorial reviewer
    #   - Review the article for clarity, accuracy, and flow
    #   - Output an improved version of the article

    # TODO: Return the three agents as a list in order.
    pass


def run_pipeline(topic: str) -> str:
    """Run the full multi-agent pipeline on a topic.

    Args:
        topic: The topic to research, write about, and review.

    Returns:
        The final reviewed article.
    """
    # TODO: Create the agents using create_agents().
    # TODO: Set the initial input to the topic string.
    # TODO: Loop through each agent, passing the previous output as input.
    # TODO: Return the final output after all agents have run.
    pass


def main():
    """Entry point: get topic from command line or use default."""
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "artificial intelligence in healthcare"

    print(f"=== Multi-Agent Pipeline ===")
    print(f"Topic: {topic}\n")

    result = run_pipeline(topic)

    print("\n=== Final Article ===\n")
    print(result)


if __name__ == "__main__":
    main()
