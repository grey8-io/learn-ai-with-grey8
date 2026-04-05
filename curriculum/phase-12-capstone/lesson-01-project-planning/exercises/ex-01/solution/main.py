"""
Exercise: Project Planning Utilities — Solution
================================================
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
        """Initialize a project plan."""
        self.name = name
        self.description = description
        self.tech_stack = tech_stack or []
        self.requirements = []
        self.milestones = []

    def add_requirement(self, requirement: str, priority: str = "medium") -> None:
        """Add a requirement to the project plan."""
        self.requirements.append({"requirement": requirement, "priority": priority})

    def add_milestone(self, name: str, tasks: list[str], deadline: str | None = None) -> None:
        """Add a milestone to the project plan."""
        self.milestones.append({"name": name, "tasks": tasks, "deadline": deadline})

    def generate_readme(self) -> str:
        """Generate a README.md template for the project."""
        lines = [
            f"# {self.name}",
            "",
            self.description,
            "",
            "## Tech Stack",
            "",
        ]

        for tech in self.tech_stack:
            lines.append(f"- {tech}")

        lines.extend([
            "",
            "## Setup",
            "",
            "1. Clone this repository",
            "2. Install dependencies: `pip install -r requirements.txt`",
            "3. Configure environment variables: `cp .env.example .env`",
            "4. Run the application",
            "",
            "## Features",
            "",
            "- Coming soon",
            "",
        ])

        return "\n".join(lines)

    def generate_structure(self) -> dict:
        """Generate a recommended directory structure."""
        structure = {
            "src": ["main.py"],
            "tests": ["test_main.py"],
            "requirements.txt": None,
            "README.md": None,
            ".env.example": None,
        }

        tech_lower = [t.lower() for t in self.tech_stack]

        if "docker" in tech_lower:
            structure["Dockerfile"] = None
            structure["docker-compose.yml"] = None

        if "fastapi" in tech_lower or "streamlit" in tech_lower:
            if "app.py" not in structure["src"]:
                structure["src"].append("app.py")

        return structure

    def estimate_complexity(self) -> str:
        """Estimate project complexity."""
        req_count = len(self.requirements)
        mile_count = len(self.milestones)

        if req_count <= 3 and mile_count <= 2:
            return "small"
        elif req_count > 8 or mile_count > 4:
            return "large"
        else:
            return "medium"


def select_project(interests: list[str], skill_level: str) -> list[dict]:
    """Recommend top 3 capstone projects based on interests and skill level."""
    level_filter = {
        "beginner": ["beginner"],
        "intermediate": ["beginner", "intermediate"],
        "advanced": ["beginner", "intermediate", "advanced"],
    }

    allowed_levels = level_filter.get(skill_level, ["beginner"])

    scored = []
    for project in CAPSTONE_PROJECTS:
        if project["level"] not in allowed_levels:
            continue

        matching_tags = [tag for tag in project["tags"] if tag in interests]
        score = len(matching_tags)

        if score > 0:
            scored.append({
                "name": project["name"],
                "level": project["level"],
                "score": score,
                "reason": f"Matches your interests: {', '.join(matching_tags)}",
            })

    scored.sort(key=lambda x: x["score"], reverse=True)

    return [
        {"name": s["name"], "level": s["level"], "reason": s["reason"]}
        for s in scored[:3]
    ]


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
