"""
Exercise: Showcase & Deployment Utilities
==========================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utilities for showcasing and deploying AI capstone projects.
"""

from datetime import datetime


class ProjectShowcase:
    """Generates showcase materials for an AI project."""

    def __init__(
        self,
        project_name: str,
        description: str,
        tech_stack: list[str],
        github_url: str | None = None,
    ):
        """Initialize the showcase.

        Args:
            project_name: Name of the project.
            description: Brief project description.
            tech_stack: List of technologies used.
            github_url: Optional GitHub repository URL.
        """
        # TODO: Store all attributes.
        pass

    def generate_demo_script(self, steps: list[dict]) -> str:
        """Generate a markdown demo walkthrough.

        Args:
            steps: List of dicts with:
                - step (str): Step description
                - command_or_action (str): What to do
                - expected_output (str): What should happen

        Returns:
            A markdown string with numbered steps, each showing
            the action and expected output.

        Format:
            # Demo: {project_name}

            ## Step 1: {step}
            ```
            {command_or_action}
            ```
            **Expected:** {expected_output}

            ## Step 2: ...
        """
        # TODO: Implement this method.
        pass

    def generate_architecture_diagram(self, components: list[dict]) -> str:
        """Generate an ASCII art architecture diagram.

        Args:
            components: List of dicts with:
                - name (str): Component name
                - type (str): Component type (e.g., "frontend", "backend", "database")
                - connects_to (list[str]): Names of components it connects to

        Returns:
            A string with:
            - Title: "Architecture: {project_name}"
            - Each component on its own line as: [{name}] ({type})
            - Connections listed as: {name} --> {target}
        """
        # TODO: Implement this method.
        pass

    def generate_portfolio_entry(self) -> str:
        """Generate a formatted markdown portfolio entry.

        Returns:
            A markdown string with:
            - ## {project_name}
            - Description
            - **Tech Stack:** comma-separated list
            - **GitHub:** link (if provided)
        """
        # TODO: Implement this method.
        pass

    def generate_deployment_checklist(self) -> str:
        """Generate a deployment checklist based on tech stack.

        Returns:
            A markdown checklist with items relevant to the tech stack.
            Always include:
            - [ ] All tests pass
            - [ ] README is up to date
            - [ ] Environment variables documented
            - [ ] Error handling in place

            If "docker" in tech_stack:
            - [ ] Docker image builds successfully
            - [ ] Docker Compose tested locally

            If "fastapi" or "streamlit" in tech_stack:
            - [ ] Health check endpoint works
            - [ ] CORS configured (if needed)
        """
        # TODO: Implement this method.
        pass


def generate_license(license_type: str = "MIT", author: str = "", year: int | None = None) -> str:
    """Generate license text.

    Args:
        license_type: "MIT" or "Apache-2.0".
        author: Author name for the license.
        year: Year for the copyright. Defaults to current year.

    Returns:
        The license text as a string.
        For MIT: standard MIT license template with year and author.
        For Apache-2.0: short Apache 2.0 notice with year and author.

    Raises:
        ValueError: If license_type is not recognized.
    """
    # TODO: Implement this function.
    pass


def create_changelog(entries: list[dict]) -> str:
    """Generate a CHANGELOG.md formatted string.

    Args:
        entries: List of dicts with:
            - version (str): Version number (e.g., "1.0.0")
            - date (str): Release date (e.g., "2025-03-01")
            - changes (list[str]): List of change descriptions

    Returns:
        A CHANGELOG.md formatted string with:
        # Changelog

        ## v{version} - {date}
        - {change1}
        - {change2}

        ## v{version} - {date}
        ...
    """
    # TODO: Implement this function.
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    showcase = ProjectShowcase(
        "AI Flashcard Generator",
        "Generate study flashcards from any topic using local LLMs",
        ["python", "ollama", "streamlit", "docker"],
        github_url="https://github.com/user/ai-flashcards",
    )

    print("=== Demo Script ===")
    print(showcase.generate_demo_script([
        {"step": "Start the app", "command_or_action": "docker compose up", "expected_output": "App running on http://localhost:8501"},
        {"step": "Generate flashcards", "command_or_action": "Enter topic: Python basics", "expected_output": "5 flashcards generated"},
    ]))
    print()

    print("=== Architecture ===")
    print(showcase.generate_architecture_diagram([
        {"name": "Streamlit UI", "type": "frontend", "connects_to": ["FastAPI"]},
        {"name": "FastAPI", "type": "backend", "connects_to": ["Ollama"]},
        {"name": "Ollama", "type": "model_server", "connects_to": []},
    ]))
    print()

    print("=== Portfolio Entry ===")
    print(showcase.generate_portfolio_entry())
    print()

    print("=== Deployment Checklist ===")
    print(showcase.generate_deployment_checklist())
    print()

    print("=== License ===")
    print(generate_license("MIT", "Jane Developer", 2025)[:200] + "...")
    print()

    print("=== Changelog ===")
    print(create_changelog([
        {"version": "1.0.0", "date": "2025-03-01", "changes": ["Initial release", "CLI flashcard generation"]},
        {"version": "1.1.0", "date": "2025-03-15", "changes": ["Added Streamlit UI", "Fixed timeout handling"]},
    ]))
