"""
Exercise: Project Planning Utilities
======================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utilities for planning AI capstone projects.
"""


# ---------------------------------------------------------------------------
# Capstone project catalog (used by select_project)
# ---------------------------------------------------------------------------
CAPSTONE_PROJECTS = [
    {"id": 1, "name": "AI Flashcard Generator", "level": "beginner", "tags": ["education", "cli", "llm"]},
    {"id": 2, "name": "Mood Journal with AI Insights", "level": "beginner", "tags": ["health", "journal", "llm"]},
    {"id": 3, "name": "Recipe Generator", "level": "beginner", "tags": ["food", "cli", "llm"]},
    {"id": 4, "name": "Daily Standup Bot", "level": "beginner", "tags": ["productivity", "cli", "llm"]},
    {"id": 5, "name": "Code Comment Generator", "level": "beginner", "tags": ["code", "cli", "llm"]},
    {"id": 6, "name": "Personal Knowledge Base", "level": "intermediate", "tags": ["rag", "search", "web"]},
    {"id": 7, "name": "AI Meeting Summarizer", "level": "intermediate", "tags": ["productivity", "summarization", "web"]},
    {"id": 8, "name": "Smart Email Drafter", "level": "intermediate", "tags": ["productivity", "writing", "web"]},
    {"id": 9, "name": "Documentation Generator", "level": "intermediate", "tags": ["code", "writing", "cli"]},
    {"id": 10, "name": "Interview Prep Coach", "level": "intermediate", "tags": ["education", "chat", "web"]},
    {"id": 11, "name": "Multi-Agent Research Assistant", "level": "advanced", "tags": ["agents", "research", "rag"]},
    {"id": 12, "name": "AI-Powered Code Reviewer", "level": "advanced", "tags": ["code", "agents", "web"]},
    {"id": 13, "name": "Custom Chatbot Platform", "level": "advanced", "tags": ["chat", "rag", "web", "deployment"]},
    {"id": 14, "name": "AI Content Pipeline", "level": "advanced", "tags": ["agents", "writing", "automation"]},
    {"id": 15, "name": "Local AI Development Environment", "level": "advanced", "tags": ["code", "agents", "tools"]},
]


class ProjectPlan:
    """A project planning tool for AI capstone projects."""

    def __init__(self, name: str, description: str, tech_stack: list[str] | None = None):
        """Initialize a project plan.

        Args:
            name: Project name.
            description: Brief project description.
            tech_stack: List of technologies (e.g., ["python", "fastapi", "ollama"]).
        """
        # TODO: Store name, description, tech_stack (default to empty list).
        # Also initialize empty lists for requirements and milestones.
        pass

    def add_requirement(self, requirement: str, priority: str = "medium") -> None:
        """Add a requirement to the project plan.

        Args:
            requirement: Description of the requirement.
            priority: "high", "medium", or "low".
        """
        # TODO: Append a dict with requirement and priority to self.requirements.
        pass

    def add_milestone(self, name: str, tasks: list[str], deadline: str | None = None) -> None:
        """Add a milestone to the project plan.

        Args:
            name: Milestone name (e.g., "MVP", "V2").
            tasks: List of task descriptions.
            deadline: Optional deadline string.
        """
        # TODO: Append a dict with name, tasks, and deadline to self.milestones.
        pass

    def generate_readme(self) -> str:
        """Generate a README.md template for the project.

        Returns:
            A markdown string with:
            - # {name}
            - Description
            - ## Tech Stack (bulleted list)
            - ## Setup (placeholder text)
            - ## Features (placeholder text)
        """
        # TODO: Implement this method.
        # Build a markdown README string using self.name, self.description, self.tech_stack.
        pass

    def generate_structure(self) -> dict:
        """Generate a recommended directory structure.

        Returns:
            A dict representing the directory tree. Always includes:
            {
                "src": ["main.py"],
                "tests": ["test_main.py"],
                "requirements.txt": None,
                "README.md": None,
                ".env.example": None,
            }
            If "docker" in tech_stack, add "Dockerfile": None and "docker-compose.yml": None.
            If "fastapi" or "streamlit" in tech_stack, add "src" entry with "app.py".
        """
        # TODO: Implement this method.
        pass

    def estimate_complexity(self) -> str:
        """Estimate project complexity based on requirements and milestones.

        Returns:
            "small" if requirements <= 3 and milestones <= 2
            "large" if requirements > 8 or milestones > 4
            "medium" otherwise
        """
        # TODO: Implement this method.
        pass


def select_project(interests: list[str], skill_level: str) -> list[dict]:
    """Recommend top 3 capstone projects based on interests and skill level.

    Args:
        interests: List of interest keywords (e.g., ["code", "education"]).
        skill_level: "beginner", "intermediate", or "advanced".

    Returns:
        List of up to 3 dicts, each with:
            - name (str): Project name
            - level (str): Project difficulty level
            - reason (str): Why this project was recommended

    Selection logic:
        1. Filter projects by skill level:
           - "beginner" -> only "beginner" projects
           - "intermediate" -> "beginner" and "intermediate" projects
           - "advanced" -> all projects
        2. Score each project by counting matching interest tags.
        3. Sort by score descending, take top 3.
        4. For the reason, list which interests matched.
    """
    # TODO: Implement this function.
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    plan = ProjectPlan(
        "AI Flashcard Generator",
        "Generate study flashcards from any topic using LLMs",
        ["python", "ollama", "streamlit"],
    )
    plan.add_requirement("Generate flashcards from a topic", "high")
    plan.add_requirement("Save and load flashcard decks", "medium")
    plan.add_requirement("Quiz mode with scoring", "low")
    plan.add_milestone("MVP", ["Basic CLI flashcard generation", "Simple prompt template"])
    plan.add_milestone("V2", ["Streamlit UI", "Deck persistence"], deadline="2025-03-01")

    print("=== README ===")
    print(plan.generate_readme())
    print()

    print("=== Structure ===")
    import json
    print(json.dumps(plan.generate_structure(), indent=2))
    print()

    print("=== Complexity ===")
    print(plan.estimate_complexity())
    print()

    print("=== Project Recommendations ===")
    recs = select_project(["code", "education"], "intermediate")
    for r in recs:
        print(f"  - {r['name']} ({r['level']}): {r['reason']}")
