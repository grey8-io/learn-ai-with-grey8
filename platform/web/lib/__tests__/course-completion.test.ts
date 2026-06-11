import fs from "fs";
import path from "path";
import {
  isCourseComplete,
  getCourseBadgeSrc,
  getCourseLinkedInShareUrl,
  hasShownCourseBadge,
  markCourseBadgeShown,
  decideCompletionBadges,
  type CompletionManifest,
  type DecisionPhase,
} from "../course-completion";

const REPO_ROOT = path.join(__dirname, "..", "..", "..", "..");
const MANIFEST_PATH = path.join(REPO_ROOT, "curriculum", "manifest.json");

function loadRealManifest(): CompletionManifest {
  return JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf-8"));
}

function allLessonIds(m: CompletionManifest): string[] {
  return m.phases.flatMap((ph) => ph.lessons.map((l) => l.id));
}

describe("isCourseComplete — synthetic", () => {
  const manifest: CompletionManifest = {
    phases: [
      { lessons: [{ id: "p1/l1" }, { id: "p1/l2" }] },
      { lessons: [{ id: "p2/l1" }] },
    ],
  };

  it("is false for an empty manifest (no false positive from [].every)", () => {
    expect(isCourseComplete({ phases: [] }, [])).toBe(false);
    expect(isCourseComplete({ phases: [{ lessons: [] }] }, [])).toBe(false);
  });

  it("is false when any lesson is missing", () => {
    expect(isCourseComplete(manifest, ["p1/l1", "p1/l2"])).toBe(false);
    expect(isCourseComplete(manifest, ["p1/l1", "p2/l1"])).toBe(false);
  });

  it("is true only when every lesson of every phase is completed", () => {
    expect(isCourseComplete(manifest, ["p1/l1", "p1/l2", "p2/l1"])).toBe(true);
  });

  it("accepts both a Set and an array", () => {
    const ids = ["p1/l1", "p1/l2", "p2/l1"];
    expect(isCourseComplete(manifest, new Set(ids))).toBe(true);
    expect(isCourseComplete(manifest, ids)).toBe(true);
  });

  it("ignores extra/unknown completed ids", () => {
    expect(
      isCourseComplete(manifest, ["p1/l1", "p1/l2", "p2/l1", "ghost/l9"])
    ).toBe(true);
  });
});

describe("isCourseComplete — real curriculum manifest (integration)", () => {
  const manifest = loadRealManifest();
  const ids = allLessonIds(manifest);

  it("reflects the real curriculum size (12 phases / 39 lessons)", () => {
    expect(manifest.phases.length).toBe(12);
    expect(ids.length).toBe(39);
  });

  it("completing EVERY real lesson marks the course complete", () => {
    expect(isCourseComplete(manifest, ids)).toBe(true);
  });

  it("missing even one real lesson keeps it incomplete", () => {
    expect(isCourseComplete(manifest, ids.slice(0, ids.length - 1))).toBe(false);
  });

  it("having only the first phase done is not complete", () => {
    const firstPhase = manifest.phases[0].lessons.map((l) => l.id);
    expect(isCourseComplete(manifest, firstPhase)).toBe(false);
  });
});

describe("course badge asset + LinkedIn share", () => {
  it("points at a badge image that actually exists on disk", () => {
    const src = getCourseBadgeSrc();
    expect(src).toBe("/badges/course-complete.png");
    const file = path.join(REPO_ROOT, "platform", "web", "public", src);
    expect(fs.existsSync(file)).toBe(true);
  });

  it("builds a valid LinkedIn share URL with the repo link and message", () => {
    const url = getCourseLinkedInShareUrl();
    expect(url.startsWith("https://www.linkedin.com/sharing/share-offsite/?")).toBe(
      true
    );
    // Parses as a URL and carries the repo + a non-empty summary.
    const parsed = new URL(url);
    expect(parsed.searchParams.get("url")).toBe(
      "https://github.com/grey8-io/learn-ai-with-grey8"
    );
    const summary = parsed.searchParams.get("summary") ?? "";
    expect(summary).toContain("Learn AI With Grey8");
    expect(summary).toContain("github.com/grey8-io/learn-ai-with-grey8");
    expect(summary).toContain("#LearnAI");
  });
});

describe("decideCompletionBadges", () => {
  // Two two-lesson phases — small enough to reason about exhaustively.
  const phases: DecisionPhase[] = [
    { phase: 1, title: "Phase One", lessons: [{ id: "p1/l1" }, { id: "p1/l2" }] },
    { phase: 2, title: "Phase Two", lessons: [{ id: "p2/l1" }, { id: "p2/l2" }] },
  ];
  const ALL = ["p1/l1", "p1/l2", "p2/l1", "p2/l2"];

  it("does nothing when the current phase isn't fully complete", () => {
    const d = decideCompletionBadges({
      phases,
      completedLessonIds: ["p1/l1"],
      currentPhase: 1,
      phaseBadgeAlreadyShown: false,
      courseBadgeAlreadyShown: false,
    });
    expect(d).toEqual({
      showPhaseBadge: false,
      phaseTitle: null,
      showCourseBadge: false,
      achievements: [],
    });
  });

  it("shows only the phase badge when a non-final phase completes", () => {
    const d = decideCompletionBadges({
      phases,
      completedLessonIds: ["p1/l1", "p1/l2"],
      currentPhase: 1,
      phaseBadgeAlreadyShown: false,
      courseBadgeAlreadyShown: false,
    });
    expect(d.showPhaseBadge).toBe(true);
    expect(d.phaseTitle).toBe("Phase One");
    expect(d.showCourseBadge).toBe(false);
    expect(d.achievements).toContain("phase_crusher");
    expect(d.achievements).not.toContain("full_stack");
  });

  it("shows BOTH when the final phase completes the whole course", () => {
    const d = decideCompletionBadges({
      phases,
      completedLessonIds: ALL,
      currentPhase: 2,
      phaseBadgeAlreadyShown: false,
      courseBadgeAlreadyShown: false,
    });
    expect(d.showPhaseBadge).toBe(true);
    expect(d.phaseTitle).toBe("Phase Two");
    expect(d.showCourseBadge).toBe(true);
    expect(d.achievements).toEqual(
      expect.arrayContaining(["phase_crusher", "full_stack"])
    );
  });

  it("retroactive graduate: course-only when phase badges were already shown", () => {
    // Existing learner who finished before this feature existed: every phase
    // badge already celebrated, but the course finale never was.
    const d = decideCompletionBadges({
      phases,
      completedLessonIds: ALL,
      currentPhase: 2,
      phaseBadgeAlreadyShown: true,
      courseBadgeAlreadyShown: false,
    });
    expect(d.showPhaseBadge).toBe(false);
    expect(d.showCourseBadge).toBe(true);
    expect(d.achievements).toEqual(["full_stack"]);
  });

  it("out-of-order: finishing an EARLIER phase last still triggers the finale", () => {
    // Learner did phase 2 first (its badge already shown), now finishes the
    // last lesson of phase 1 — which happens to complete the whole course.
    const d = decideCompletionBadges({
      phases,
      completedLessonIds: ALL,
      currentPhase: 1,
      phaseBadgeAlreadyShown: false, // phase 1's badge not yet shown
      courseBadgeAlreadyShown: false,
    });
    expect(d.showPhaseBadge).toBe(true);
    expect(d.phaseTitle).toBe("Phase One");
    expect(d.showCourseBadge).toBe(true);
  });

  it("never re-fires once both badges have been shown", () => {
    const d = decideCompletionBadges({
      phases,
      completedLessonIds: ALL,
      currentPhase: 2,
      phaseBadgeAlreadyShown: true,
      courseBadgeAlreadyShown: true,
    });
    expect(d.showPhaseBadge).toBe(false);
    expect(d.showCourseBadge).toBe(false);
    expect(d.achievements).toEqual([]);
  });

  it("adds five_phases once five or more phases are complete", () => {
    const five: DecisionPhase[] = [1, 2, 3, 4, 5].map((n) => ({
      phase: n,
      title: `Phase ${n}`,
      lessons: [{ id: `p${n}/l1` }],
    }));
    const d = decideCompletionBadges({
      phases: five,
      completedLessonIds: five.map((p) => p.lessons[0].id),
      currentPhase: 5,
      phaseBadgeAlreadyShown: false,
      courseBadgeAlreadyShown: false,
    });
    expect(d.achievements).toEqual(
      expect.arrayContaining(["phase_crusher", "five_phases", "full_stack"])
    );
  });
});

describe("idempotency helpers (localStorage)", () => {
  beforeEach(() => localStorage.clear());

  it("starts unshown, then sticks once marked", () => {
    expect(hasShownCourseBadge()).toBe(false);
    markCourseBadgeShown();
    expect(hasShownCourseBadge()).toBe(true);
    // Marking again is harmless and stays true.
    markCourseBadgeShown();
    expect(hasShownCourseBadge()).toBe(true);
  });
});
