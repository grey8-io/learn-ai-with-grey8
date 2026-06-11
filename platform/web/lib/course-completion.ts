/**
 * Course-completion helpers — pure logic shared by the lesson page (which
 * decides when to fire the finale) and the CourseCompleteModal (which renders
 * the badge + LinkedIn share).
 *
 * Kept free of React/JSX and the "@/" alias so it can be unit-tested directly
 * (including an integration check against the real curriculum manifest).
 */

const REPO_URL = "https://github.com/grey8-io/learn-ai-with-grey8";

/** Minimal shape we need from the manifest — decoupled from lib/api types so
 *  tests can construct fixtures without the full Manifest interface. */
export interface CompletionManifest {
  phases: { lessons: { id: string }[] }[];
}

/** Manifest phase shape with the fields the badge decision reads. */
export interface DecisionPhase {
  phase: number;
  title: string;
  lessons: { id: string }[];
}

export interface DecideBadgesInput {
  phases: DecisionPhase[];
  completedLessonIds: Set<string> | Iterable<string>;
  /** Phase number of the lesson that was just completed. */
  currentPhase: number;
  /** Whether THIS phase's badge was already celebrated (localStorage). */
  phaseBadgeAlreadyShown: boolean;
  /** Whether the course finale was already celebrated (localStorage). */
  courseBadgeAlreadyShown: boolean;
}

export interface BadgeDecision {
  showPhaseBadge: boolean;
  /** Title of the just-completed phase, when showPhaseBadge is true. */
  phaseTitle: string | null;
  showCourseBadge: boolean;
  /** Achievement ids to unlock as a side effect of this completion. */
  achievements: string[];
}

/**
 * Pure decision for which celebration(s) a completion should trigger. Mirrors
 * (and is the single source of truth for) the lesson page's badge logic, so
 * the WHEN — including phase-out-of-order and already-graduated learners — is
 * unit-testable without rendering the page.
 *
 * Notes:
 * - The course check is independent of `currentPhase`: the "all phases done"
 *   moment can land on any lesson, and existing graduates (whose phase badges
 *   were shown before this feature existed) retroactively get the finale via
 *   the `showCourseBadge && !showPhaseBadge` path.
 * - Sequencing (finale follows the phase badge) is the caller's concern; this
 *   function only decides what is warranted.
 */
export function decideCompletionBadges(input: DecideBadgesInput): BadgeDecision {
  const completed =
    input.completedLessonIds instanceof Set
      ? input.completedLessonIds
      : new Set(input.completedLessonIds);

  const phaseComplete = (ph: DecisionPhase): boolean =>
    ph.lessons.every((l) => completed.has(l.id));

  const decision: BadgeDecision = {
    showPhaseBadge: false,
    phaseTitle: null,
    showCourseBadge: false,
    achievements: [],
  };

  if (!input.phaseBadgeAlreadyShown) {
    const phase = input.phases.find((ph) => ph.phase === input.currentPhase);
    if (phase && phaseComplete(phase)) {
      decision.showPhaseBadge = true;
      decision.phaseTitle = phase.title;
      decision.achievements.push("phase_crusher");
      if (input.phases.filter(phaseComplete).length >= 5) {
        decision.achievements.push("five_phases");
      }
    }
  }

  if (
    !input.courseBadgeAlreadyShown &&
    isCourseComplete({ phases: input.phases }, completed)
  ) {
    decision.showCourseBadge = true;
    if (!decision.achievements.includes("full_stack")) {
      decision.achievements.push("full_stack");
    }
  }

  return decision;
}

/** Path to the course-completion badge image (served from /public). */
export function getCourseBadgeSrc(): string {
  return "/badges/course-complete.png";
}

/**
 * True only when EVERY lesson of EVERY phase is in the completed set.
 *
 * Guards against the empty-manifest false positive: `[].every()` is `true`, so
 * a manifest with no phases/lessons would otherwise report "complete". We
 * require at least one lesson to exist before it can be considered finished.
 */
export function isCourseComplete(
  manifest: CompletionManifest,
  completedLessonIds: Set<string> | Iterable<string>
): boolean {
  const completed =
    completedLessonIds instanceof Set
      ? completedLessonIds
      : new Set(completedLessonIds);

  const phases = manifest?.phases ?? [];
  const totalLessons = phases.reduce((n, ph) => n + ph.lessons.length, 0);
  if (totalLessons === 0) return false;

  return phases.every((ph) => ph.lessons.every((l) => completed.has(l.id)));
}

/** LinkedIn share URL for the whole-bootcamp finale. */
export function getCourseLinkedInShareUrl(): string {
  const text =
    "I just completed the entire Learn AI With Grey8 bootcamp — a free, " +
    "open-source AI program covering 39 lessons across 12 phases, from Python " +
    "fundamentals to deploying AI agents. Everything runs 100% locally, with " +
    "no cloud API keys or paid subscriptions.\n\n" +
    "If you want to learn to build real AI applications, start here:\n" +
    `${REPO_URL}\n\n` +
    "#LearnAI #OpenSource #Grey8 #AIBootcamp #ArtificialIntelligence";
  return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(
    REPO_URL
  )}&summary=${encodeURIComponent(text)}`;
}

/** localStorage key tracking whether the finale modal has already been shown. */
const SHOWN_KEY = "badges:course_shown";

export function hasShownCourseBadge(): boolean {
  if (typeof window === "undefined") return true;
  try {
    return localStorage.getItem(SHOWN_KEY) === "1";
  } catch {
    return false;
  }
}

export function markCourseBadgeShown(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(SHOWN_KEY, "1");
  } catch {
    // ignore — sharing is best-effort, never block completion on storage
  }
}
