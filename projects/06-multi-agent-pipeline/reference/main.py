"""
Project 06: Multi-Agent Pipeline (Reference)

Chain specialized AI agents to research, write, and review content.
Each agent is an LLM call with a focused system prompt.
"""

import sys
import requests

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"


def chat(system_prompt: str, user_message: str) -> str:
    """Send a chat request to Ollama and return the assistant's response."""
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
        },
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


class Agent:
    """A specialized AI agent with a name and system prompt."""

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    def run(self, input_text: str) -> str:
        """Run this agent on the given input and return the output."""
        print(f"[{self.name}] Working...")
        result = chat(self.system_prompt, input_text)
        print(f"[{self.name}] Done ({len(result)} chars)\n")
        return result


def create_agents() -> list:
    """Create the three pipeline agents in order."""
    researcher = Agent(
        name="Researcher",
        system_prompt=(
            "You are a research analyst. Given a topic, gather the most important "
            "facts, statistics, trends, and diverse perspectives. Output a structured "
            "research brief with bullet points organized by subtopic. Be thorough "
            "but concise. Focus on accuracy and covering multiple angles."
        ),
    )

    writer = Agent(
        name="Writer",
        system_prompt=(
            "You are a skilled article writer. You receive research notes and must "
            "write a well-structured article with:\n"
            "- A compelling introduction\n"
            "- 3-4 body sections with clear headings\n"
            "- A thoughtful conclusion\n"
            "Write in a professional but accessible tone. Use the research provided "
            "as your source material. Do not invent facts beyond what is provided."
        ),
    )

    reviewer = Agent(
        name="Reviewer",
        system_prompt=(
            "You are an editorial reviewer. You receive a draft article and must:\n"
            "1. Check for clarity and logical flow\n"
            "2. Improve awkward phrasing\n"
            "3. Ensure the introduction hooks the reader\n"
            "4. Verify the conclusion ties everything together\n"
            "Output the improved version of the full article. Do not add commentary "
            "— just output the polished article."
        ),
    )

    return [researcher, writer, reviewer]


def run_pipeline(topic: str) -> str:
    """Run the full multi-agent pipeline on a topic."""
    agents = create_agents()

    # The topic is the initial input; each agent transforms it further
    current_text = topic
    for agent in agents:
        current_text = agent.run(current_text)

    return current_text


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
