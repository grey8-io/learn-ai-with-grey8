import {
  defaultState,
  reconcileAchievements,
  achievementProgress,
  type ProgressFacts,
} from "../gamification";

beforeEach(() => localStorage.clear());

const facts = (over: Partial<ProgressFacts> = {}): ProgressFacts => ({
  lessonsCompleted: 0,
  totalLessons: 39,
  phasesCompleted: 0,
  streakDays: 0,
  visitedProjects: false,
  ...over,
});

describe("reconcileAchievements", () => {
  it("unlocks Halfway There at 50% of lessons", () => {
    const state = defaultState();
    // 19/39 is below 50% (needs >= 19.5), 20/39 clears it.
    expect(
      reconcileAchievements(state, facts({ lessonsCompleted: 19 })).map((a) => a.id)
    ).not.toContain("halfway");

    const state2 = defaultState();
    expect(
      reconcileAchievements(state2, facts({ lessonsCompleted: 20 })).map((a) => a.id)
    ).toContain("halfway");
  });

  it("unlocks phase + five-phase + full-stack milestones by phase count", () => {
    const state = defaultState();
    const ids = reconcileAchievements(state, facts({ phasesCompleted: 12 })).map(
      (a) => a.id
    );
    expect(ids).toEqual(
      expect.arrayContaining(["phase_crusher", "five_phases", "full_stack"])
    );
  });

  it("unlocks Project Starter only when the projects page was visited", () => {
    const a = defaultState();
    expect(reconcileAchievements(a, facts()).map((x) => x.id)).not.toContain(
      "project_starter"
    );
    const b = defaultState();
    expect(
      reconcileAchievements(b, facts({ visitedProjects: true })).map((x) => x.id)
    ).toContain("project_starter");
  });

  it("is idempotent — a second pass with the same facts unlocks nothing new", () => {
    const state = defaultState();
    const f = facts({ lessonsCompleted: 39, phasesCompleted: 12, streakDays: 30 });
    const first = reconcileAchievements(state, f);
    expect(first.length).toBeGreaterThan(0);
    expect(reconcileAchievements(state, f)).toEqual([]);
  });

  it("never removes or downgrades an already-unlocked achievement", () => {
    const state = defaultState();
    reconcileAchievements(state, facts({ phasesCompleted: 12 }));
    const before = [...state.unlockedAchievements];
    // A later pass with WORSE facts must not strip anything.
    reconcileAchievements(state, facts({ phasesCompleted: 0 }));
    expect(state.unlockedAchievements).toEqual(expect.arrayContaining(before));
  });
});

describe("achievementProgress", () => {
  const state = defaultState();

  it("reports lesson progress toward Halfway There against the real total", () => {
    const p = achievementProgress("halfway", facts({ lessonsCompleted: 10 }), state);
    expect(p).toEqual({ current: 10, target: 20, unit: "lessons" }); // ceil(39/2)
  });

  it("clamps progress at the target", () => {
    const p = achievementProgress("streak_3", facts({ streakDays: 9 }), state);
    expect(p).toEqual({ current: 3, target: 3, unit: "days" });
  });

  it("returns XP-based progress for level badges", () => {
    const leveled = defaultState();
    leveled.totalXP = 1000;
    const p = achievementProgress("level_5", facts(), leveled);
    expect(p).toEqual({ current: 1000, target: 2200, unit: "XP" });
  });

  it("returns null for single-action badges (no progress bar)", () => {
    for (const id of ["first_quiz", "perfect_quiz", "no_hints", "speed_learner", "project_starter"]) {
      expect(achievementProgress(id, facts(), state)).toBeNull();
    }
  });
});
