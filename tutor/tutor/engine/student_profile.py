"""Build a concise text profile from student data for LLM injection."""

from tutor.models.schemas import StudentProfile


def profile_to_text(profile: StudentProfile | None) -> str:
    """Convert a StudentProfile into a ~100-token text block for the system prompt.

    Returns empty string if no profile is provided.
    """
    if not profile:
        return ""

    lines = [
        "=== Student Profile ===",
        f"Level: {profile.level or 'New Learner'} | "
        f"Streak: {profile.streak_days} day{'s' if profile.streak_days != 1 else ''} | "
        f"Progress: {profile.lessons_completed}/{profile.total_lessons} lessons (Phase {profile.current_phase})",
    ]

    if profile.strong_topics:
        lines.append(f"Strong in: {', '.join(profile.strong_topics)}")

    if profile.weak_topics:
        lines.append(f"Needs help with: {', '.join(profile.weak_topics)}")

    if profile.exercise_attempts > 0:
        lines.append(
            f"Exercise style: {profile.exercise_attempts} submissions, "
            f"avg {profile.exercise_hint_avg:.1f} hints/exercise"
        )

    # Guidance for the tutor based on profile
    if profile.lessons_completed == 0:
        lines.append("→ This is a brand new student. Be extra encouraging and use simple language.")
    elif profile.weak_topics:
        weak = profile.weak_topics[0]
        lines.append(f"→ Student struggles with {weak}. If the question relates, break it down further.")
    if profile.exercise_hint_avg > 2.0:
        lines.append("→ Student uses many hints. Proactively offer small steps before they get stuck.")
    elif profile.exercise_hint_avg < 0.5 and profile.exercise_attempts > 3:
        lines.append("→ Student rarely uses hints. They prefer figuring things out — challenge them more.")

    return "\n".join(lines)
