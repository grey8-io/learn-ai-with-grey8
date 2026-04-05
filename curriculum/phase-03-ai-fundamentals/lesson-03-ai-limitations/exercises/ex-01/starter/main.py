"""
Exercise: AI Fact Checker
===========================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a simple fact-checker that verifies AI-generated claims against
a set of known facts.
"""


# TODO: Write a function called `fact_checker` that:
#       - Takes two parameters:
#         * claims (list[str]): A list of AI-generated claims to check
#         * known_facts (dict[str, str]): A dict mapping topics to verified facts
#           Example: {"capital_of_france": "The capital of France is Paris"}
#       - Returns a list of dicts, one per claim, with keys:
#         * "claim": the original claim string
#         * "status": one of "verified", "contradicted", or "unverified"
#         * "reason": explanation string
#       - Logic:
#         * For each claim, check if any known fact's VALUE is contained
#           in the claim (case-insensitive), OR if the claim is contained
#           in any known fact's value (case-insensitive)
#         * If a match is found: status = "verified",
#           reason = "Matches known fact: {the matching fact value}"
#         * If a known fact's KEY/topic appears in the claim (case-insensitive)
#           but the values don't match: status = "contradicted",
#           reason = "Contradicts known fact: {the matching fact value}"
#         * If no known fact is relevant: status = "unverified",
#           reason = "No matching facts available"


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    claims = [
        "The capital of France is Paris",
        "The capital of France is London",
        "Water boils at 100 degrees Celsius",
        "Elephants can fly",
    ]
    known_facts = {
        "capital_of_france": "The capital of France is Paris",
        "boiling_point": "Water boils at 100 degrees Celsius",
    }
    results = fact_checker(claims, known_facts)
    for r in results:
        print(f"  [{r['status'].upper()}] {r['claim']}")
        print(f"    Reason: {r['reason']}\n")
