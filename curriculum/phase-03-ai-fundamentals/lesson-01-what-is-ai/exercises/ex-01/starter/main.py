"""
Exercise: Classify ML Problems
================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Given a description of a machine learning problem, classify it as one of:
- "supervised"
- "unsupervised"
- "reinforcement"
"""


# Here are the problem descriptions and their correct classifications.
# Study these to understand the patterns, then implement the function below.
#
# SUPERVISED examples (learning from labeled data):
#   - "predict house prices based on features like size and location"
#   - "classify emails as spam or not spam"
#   - "diagnose diseases from medical images with known labels"
#
# UNSUPERVISED examples (finding patterns without labels):
#   - "group customers into segments based on purchasing behavior"
#   - "detect anomalies in network traffic"
#   - "discover topics in a collection of news articles"
#
# REINFORCEMENT examples (learning from rewards/penalties):
#   - "train a robot to navigate a maze"
#   - "teach an AI to play chess by playing against itself"
#   - "optimize traffic light timing to reduce congestion"


# TODO: Write a function called `classify_ml_problem` that:
#       - Takes one parameter: description (str)
#       - Returns one of: "supervised", "unsupervised", "reinforcement"
#       - Use keyword matching to determine the type:
#         * Supervised keywords: "predict", "classify", "label", "diagnose", "spam"
#         * Unsupervised keywords: "group", "cluster", "segment", "anomal", "discover", "topic"
#         * Reinforcement keywords: "robot", "play", "navigate", "game", "optimize", "train a"
#       - Convert the description to lowercase before checking
#       - If no keywords match, return "unknown"


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
