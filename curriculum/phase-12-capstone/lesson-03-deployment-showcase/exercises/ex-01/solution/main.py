"""
Exercise: Showcase & Deployment Utilities — Solution
====================================================
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
        """Initialize the showcase."""
        self.project_name = project_name
        self.description = description
        self.tech_stack = tech_stack
        self.github_url = github_url

    def generate_demo_script(self, steps: list[dict]) -> str:
        """Generate a markdown demo walkthrough."""
        lines = [f"# Demo: {self.project_name}", ""]

        for i, step in enumerate(steps, 1):
            lines.extend([
                f"## Step {i}: {step['step']}",
                "```",
                step["command_or_action"],
                "```",
                f"**Expected:** {step['expected_output']}",
                "",
            ])

        return "\n".join(lines)

    def generate_architecture_diagram(self, components: list[dict]) -> str:
        """Generate an ASCII art architecture diagram."""
        lines = [f"Architecture: {self.project_name}", ""]

        lines.append("Components:")
        for comp in components:
            lines.append(f"  [{comp['name']}] ({comp['type']})")

        lines.append("")
        lines.append("Connections:")
        for comp in components:
            for target in comp.get("connects_to", []):
                lines.append(f"  {comp['name']} --> {target}")

        return "\n".join(lines)

    def generate_portfolio_entry(self) -> str:
        """Generate a formatted markdown portfolio entry."""
        lines = [
            f"## {self.project_name}",
            "",
            self.description,
            "",
            f"**Tech Stack:** {', '.join(self.tech_stack)}",
            "",
        ]

        if self.github_url:
            lines.append(f"**GitHub:** [{self.github_url}]({self.github_url})")
            lines.append("")

        return "\n".join(lines)

    def generate_deployment_checklist(self) -> str:
        """Generate a deployment checklist based on tech stack."""
        items = [
            "- [ ] All tests pass",
            "- [ ] README is up to date",
            "- [ ] Environment variables documented",
            "- [ ] Error handling in place",
        ]

        tech_lower = [t.lower() for t in self.tech_stack]

        if "docker" in tech_lower:
            items.append("- [ ] Docker image builds successfully")
            items.append("- [ ] Docker Compose tested locally")

        if "fastapi" in tech_lower or "streamlit" in tech_lower:
            items.append("- [ ] Health check endpoint works")
            items.append("- [ ] CORS configured (if needed)")

        return "# Deployment Checklist\n\n" + "\n".join(items)


def generate_license(license_type: str = "MIT", author: str = "", year: int | None = None) -> str:
    """Generate license text."""
    if year is None:
        year = datetime.now().year

    if license_type == "MIT":
        return (
            f"MIT License\n"
            f"\n"
            f"Copyright (c) {year} {author}\n"
            f"\n"
            f"Permission is hereby granted, free of charge, to any person obtaining a copy\n"
            f"of this software and associated documentation files (the \"Software\"), to deal\n"
            f"in the Software without restriction, including without limitation the rights\n"
            f"to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
            f"copies of the Software, and to permit persons to whom the Software is\n"
            f"furnished to do so, subject to the following conditions:\n"
            f"\n"
            f"The above copyright notice and this permission notice shall be included in all\n"
            f"copies or substantial portions of the Software.\n"
            f"\n"
            f"THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
            f"IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
            f"FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
            f"AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
            f"LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
            f"OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
            f"SOFTWARE."
        )
    elif license_type == "Apache-2.0":
        return (
            f"Copyright {year} {author}\n"
            f"\n"
            f"Licensed under the Apache License, Version 2.0 (the \"License\");\n"
            f"you may not use this file except in compliance with the License.\n"
            f"You may obtain a copy of the License at\n"
            f"\n"
            f"    http://www.apache.org/licenses/LICENSE-2.0\n"
            f"\n"
            f"Unless required by applicable law or agreed to in writing, software\n"
            f"distributed under the License is distributed on an \"AS IS\" BASIS,\n"
            f"WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n"
            f"See the License for the specific language governing permissions and\n"
            f"limitations under the License."
        )
    else:
        raise ValueError(f"Unsupported license type: {license_type}. Use 'MIT' or 'Apache-2.0'.")


def create_changelog(entries: list[dict]) -> str:
    """Generate a CHANGELOG.md formatted string."""
    lines = ["# Changelog", ""]

    for entry in entries:
        lines.append(f"## v{entry['version']} - {entry['date']}")
        for change in entry["changes"]:
            lines.append(f"- {change}")
        lines.append("")

    return "\n".join(lines)


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
