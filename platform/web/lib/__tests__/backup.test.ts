import { exportBackup, importBackup } from "../backup";

beforeEach(() => localStorage.clear());

function seedProgress() {
  localStorage.setItem(
    "progress:lessons",
    JSON.stringify([{ lessonId: "phase-01/lesson-01", status: "completed" }])
  );
  localStorage.setItem(
    "progress:submissions",
    JSON.stringify([{ exerciseId: "ex-01", score: 90 }])
  );
  localStorage.setItem(
    "progress:chat:phase-01/lesson-01",
    JSON.stringify([{ role: "user", content: "hi" }])
  );
  localStorage.setItem(
    "gamification:state",
    JSON.stringify({ totalXP: 1234, unlockedAchievements: ["first_blood"] })
  );
  localStorage.setItem("badges:phases_shown", JSON.stringify(["phase-01"]));
}

describe("exportBackup", () => {
  it("captures every app-owned namespace, decoded", () => {
    seedProgress();
    const backup = exportBackup();

    expect(backup.app).toBe("learn-ai-with-grey8");
    expect(backup.type).toBe("progress-backup");
    expect(Object.keys(backup.data).sort()).toEqual([
      "badges:phases_shown",
      "gamification:state",
      "progress:chat:phase-01/lesson-01",
      "progress:lessons",
      "progress:submissions",
    ]);
    // Values are decoded JSON, not raw strings.
    expect((backup.data["gamification:state"] as { totalXP: number }).totalXP).toBe(1234);
  });

  it("ignores keys outside the app namespaces", () => {
    localStorage.setItem("supabase.auth.token", "secret");
    localStorage.setItem("some-other-app", "data");
    seedProgress();

    const backup = exportBackup();
    expect(backup.data).not.toHaveProperty("supabase.auth.token");
    expect(backup.data).not.toHaveProperty("some-other-app");
  });
});

describe("importBackup", () => {
  it("round-trips: export → clear → import restores all state", () => {
    seedProgress();
    const text = JSON.stringify(exportBackup());

    localStorage.clear();
    expect(localStorage.getItem("gamification:state")).toBeNull();

    const result = importBackup(text);
    expect(result.keysRestored).toBe(5);
    expect(JSON.parse(localStorage.getItem("gamification:state")!).totalXP).toBe(1234);
    expect(JSON.parse(localStorage.getItem("progress:lessons")!)[0].status).toBe(
      "completed"
    );
  });

  it("overwrites existing values on the current browser", () => {
    seedProgress();
    const text = JSON.stringify(exportBackup());

    // Simulate a different/older state on this browser.
    localStorage.setItem(
      "gamification:state",
      JSON.stringify({ totalXP: 5, unlockedAchievements: [] })
    );

    importBackup(text);
    expect(JSON.parse(localStorage.getItem("gamification:state")!).totalXP).toBe(1234);
  });

  it("never writes keys outside the app namespaces", () => {
    const malicious = JSON.stringify({
      app: "learn-ai-with-grey8",
      type: "progress-backup",
      version: 1,
      exportedAt: "2026-01-01T00:00:00.000Z",
      data: {
        "progress:lessons": [],
        "supabase.auth.token": "injected",
        evil: "x",
      },
    });
    importBackup(malicious);
    expect(localStorage.getItem("supabase.auth.token")).toBeNull();
    expect(localStorage.getItem("evil")).toBeNull();
  });

  it("rejects non-JSON input", () => {
    expect(() => importBackup("not json{")).toThrow(/valid JSON/);
  });

  it("rejects a foreign JSON file", () => {
    expect(() => importBackup(JSON.stringify({ hello: "world" }))).toThrow(
      /Learn AI With Grey8 progress backup/
    );
  });

  it("rejects a backup with no restorable data", () => {
    const empty = JSON.stringify({
      app: "learn-ai-with-grey8",
      type: "progress-backup",
      version: 1,
      exportedAt: "2026-01-01T00:00:00.000Z",
      data: { evil: "x" }, // no app-owned keys
    });
    expect(() => importBackup(empty)).toThrow(/No progress data/);
  });
});
