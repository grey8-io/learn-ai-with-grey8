"""
Exercise: AI Fact Checker — Solution
======================================
"""


def fact_checker(claims: list[str], known_facts: dict[str, str]) -> list[dict]:
    """Check AI-generated claims against known facts.

    Args:
        claims: A list of claim strings to verify.
        known_facts: A dict mapping topic keys to verified fact strings.

    Returns:
        A list of dicts with 'claim', 'status', and 'reason' for each claim.
    """
    results = []

    for claim in claims:
        claim_lower = claim.lower()
        matched = False

        for topic, fact in known_facts.items():
            fact_lower = fact.lower()

            # Check if the fact matches the claim
            if fact_lower in claim_lower or claim_lower in fact_lower:
                results.append({
                    "claim": claim,
                    "status": "verified",
                    "reason": f"Matches known fact: {fact}",
                })
                matched = True
                break

            # Check if the topic is mentioned but fact doesn't match
            topic_words = topic.replace("_", " ").lower()
            if topic_words in claim_lower:
                results.append({
                    "claim": claim,
                    "status": "contradicted",
                    "reason": f"Contradicts known fact: {fact}",
                })
                matched = True
                break

        if not matched:
            results.append({
                "claim": claim,
                "status": "unverified",
                "reason": "No matching facts available",
            })

    return results


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
