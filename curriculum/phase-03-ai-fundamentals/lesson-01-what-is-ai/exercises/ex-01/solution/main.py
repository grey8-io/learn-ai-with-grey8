"""
Exercise: Classify ML Problems — Solution
===========================================
"""


def classify_ml_problem(description: str) -> str:
    """Classify a machine learning problem as supervised, unsupervised, or reinforcement.

    Args:
        description: A text description of the ML problem.

    Returns:
        One of 'supervised', 'unsupervised', 'reinforcement', or 'unknown'.
    """
    text = description.lower()

    supervised_keywords = ["predict", "classify", "label", "diagnose", "spam"]
    unsupervised_keywords = ["group", "cluster", "segment", "anomal", "discover", "topic"]
    reinforcement_keywords = ["robot", "play", "navigate", "game", "optimize", "train a"]

    for keyword in supervised_keywords:
        if keyword in text:
            return "supervised"

    for keyword in unsupervised_keywords:
        if keyword in text:
            return "unsupervised"

    for keyword in reinforcement_keywords:
        if keyword in text:
            return "reinforcement"

    return "unknown"


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    problems = [
        "Predict house prices based on size and location",
        "Group customers into segments based on behavior",
        "Train a robot to navigate a warehouse",
        "Classify images of cats and dogs",
        "Discover hidden topics in research papers",
    ]
    for problem in problems:
        print(f"  {problem}")
        print(f"  -> {classify_ml_problem(problem)}\n")
