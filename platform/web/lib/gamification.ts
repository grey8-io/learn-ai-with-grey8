/**
 * Gamification engine — XP, Levels, Achievements, Daily Goals.
 * All state persisted via localStorage. Computed from progress data.
 */

// ---------------------------------------------------------------------------
// Levels
// ---------------------------------------------------------------------------

export interface Level {
  rank: number;
  title: string;
  minXP: number;
  icon: string; // emoji
}

export const LEVELS: Level[] = [
  { rank: 1, title: "Beginner",   minXP: 0,    icon: "🌱" },
  { rank: 2, title: "Apprentice", minXP: 200,  icon: "📘" },
  { rank: 3, title: "Builder",    minXP: 600,  icon: "🔧" },
  { rank: 4, title: "Developer",  minXP: 1200, icon: "💻" },
  { rank: 5, title: "Engineer",   minXP: 2200, icon: "⚙️" },
  { rank: 6, title: "Architect",  minXP: 3500, icon: "🏗️" },
  { rank: 7, title: "AI Master",  minXP: 5000, icon: "🧠" },
];

export function getLevel(xp: number): Level {
  let current = LEVELS[0];
  for (const level of LEVELS) {
    if (xp >= level.minXP) current = level;
    else break;
  }
  return current;
}

export function getNextLevel(xp: number): Level | null {
  for (const level of LEVELS) {
    if (xp < level.minXP) return level;
  }
  return null; // max level reached
}

export function getLevelProgress(xp: number): number {
  const current = getLevel(xp);
  const next = getNextLevel(xp);
  if (!next) return 100;
  const range = next.minXP - current.minXP;
  const progress = xp - current.minXP;
  return Math.round((progress / range) * 100);
}

// ---------------------------------------------------------------------------
// XP Calculation
// ---------------------------------------------------------------------------

/** XP earned from a quiz score. */
export function quizXP(score: number, total: number, streakDays: number): number {
  const baseXP = Math.round((score / total) * 100); // 0-100 XP
  const multiplier = streakDays >= 3 ? 2 : 1;
  return baseXP * multiplier;
}

/** XP earned from an exercise score. */
export function exerciseXP(score: number, streakDays: number): number {
  const baseXP = Math.round(score * 1.5); // 0-150 XP for 0-100%
  const multiplier = streakDays >= 3 ? 2 : 1;
  return baseXP * multiplier;
}

/** XP earned from completing a lesson. */
export function lessonCompleteXP(streakDays: number): number {
  const baseXP = 50;
  const multiplier = streakDays >= 3 ? 2 : 1;
  return baseXP * multiplier;
}

// ---------------------------------------------------------------------------
// Achievements
// ---------------------------------------------------------------------------

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: "milestone" | "streak" | "skill" | "mastery";
}

export const ACHIEVEMENTS: Achievement[] = [
  // Milestones
  { id: "first_quiz",       title: "First Blood",       description: "Pass your first quiz",                     icon: "🎯", category: "milestone" },
  { id: "first_exercise",   title: "Code Runner",        description: "Pass your first exercise",                 icon: "▶️", category: "milestone" },
  { id: "first_lesson",     title: "Off the Ground",     description: "Complete your first lesson",               icon: "🚀", category: "milestone" },
  { id: "ten_lessons",      title: "Getting Serious",    description: "Complete 10 lessons",                      icon: "📚", category: "milestone" },
  { id: "halfway",          title: "Halfway There",      description: "Complete 50% of all lessons",              icon: "⛰️", category: "milestone" },
  { id: "full_stack",       title: "Full Stack",         description: "Complete all 12 phases",                   icon: "👑", category: "milestone" },

  // Streaks
  { id: "streak_3",         title: "On a Roll",          description: "3-day learning streak",                    icon: "🔥", category: "streak" },
  { id: "streak_7",         title: "Streak Lord",        description: "7-day learning streak",                    icon: "💪", category: "streak" },
  { id: "streak_14",        title: "Unstoppable",        description: "14-day learning streak",                   icon: "⚡", category: "streak" },
  { id: "streak_30",        title: "Iron Will",          description: "30-day learning streak",                   icon: "🏆", category: "streak" },

  // Skill
  { id: "perfect_quiz",     title: "Perfect Score",      description: "Score 100% on any quiz",                   icon: "💯", category: "skill" },
  { id: "no_hints",         title: "No Hints Needed",    description: "Pass an exercise without using hints",     icon: "🧩", category: "skill" },
  { id: "speed_learner",    title: "Speed Learner",      description: "Complete 3 lessons in one day",            icon: "⏱️", category: "skill" },

  // Mastery
  { id: "phase_crusher",    title: "Phase Crusher",      description: "Complete an entire phase",                 icon: "🎖️", category: "mastery" },
  { id: "five_phases",      title: "Halfway Master",     description: "Complete 5 phases",                        icon: "🌟", category: "mastery" },
  { id: "project_starter",  title: "Project Starter",    description: "Visit the projects page",                  icon: "📂", category: "mastery" },
  { id: "level_5",          title: "Engineer Status",    description: "Reach Level 5 (Engineer)",                 icon: "⚙️", category: "mastery" },
  { id: "level_7",          title: "AI Master",          description: "Reach Level 7 (AI Master)",                icon: "🧠", category: "mastery" },
];

// ---------------------------------------------------------------------------
// Gamification State (persisted in localStorage)
// ---------------------------------------------------------------------------

export interface GamificationState {
  totalXP: number;
  unlockedAchievements: string[]; // achievement IDs
  xpLog: XPEvent[]; // recent XP events for display
  dailyGoalDate: string; // ISO date string (YYYY-MM-DD)
  dailyLessonsCompleted: number;
  streakFreezeAvailable: boolean;
  lastStreakDate: string | null;
  hintsUsedPerExercise: Record<string, number>; // exerciseId -> hint count
}

export interface XPEvent {
  amount: number;
  reason: string;
  timestamp: string;
}

const STORAGE_KEY = "gamification:state";

export function defaultState(): GamificationState {
  return {
    totalXP: 0,
    unlockedAchievements: [],
    xpLog: [],
    dailyGoalDate: todayISO(),
    dailyLessonsCompleted: 0,
    streakFreezeAvailable: true,
    lastStreakDate: null,
    hintsUsedPerExercise: {},
  };
}

function todayISO(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export function loadState(): GamificationState {
  if (typeof window === "undefined") return defaultState();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultState();
    const state = JSON.parse(raw) as GamificationState;
    // Reset daily counter if date changed
    if (state.dailyGoalDate !== todayISO()) {
      state.dailyGoalDate = todayISO();
      state.dailyLessonsCompleted = 0;
    }
    return state;
  } catch {
    return defaultState();
  }
}

export function saveState(state: GamificationState): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // localStorage full — silently ignore
  }
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------

export interface GamificationResult {
  xpGained: number;
  newAchievements: Achievement[];
  leveledUp: boolean;
  previousLevel: Level;
  newLevel: Level;
}

/** Award XP and check for new achievements. Returns what happened. */
export function awardXP(
  state: GamificationState,
  amount: number,
  reason: string
): GamificationResult {
  const previousLevel = getLevel(state.totalXP);
  state.totalXP += amount;
  state.xpLog = [
    { amount, reason, timestamp: new Date().toISOString() },
    ...state.xpLog.slice(0, 19), // keep last 20
  ];
  const newLevel = getLevel(state.totalXP);
  const leveledUp = newLevel.rank > previousLevel.rank;
  const newAchievements = checkAchievements(state);
  saveState(state);
  return { xpGained: amount, newAchievements, leveledUp, previousLevel, newLevel };
}

/** Record a lesson completion for daily goal tracking. */
export function recordDailyLesson(state: GamificationState): void {
  if (state.dailyGoalDate !== todayISO()) {
    state.dailyGoalDate = todayISO();
    state.dailyLessonsCompleted = 0;
  }
  state.dailyLessonsCompleted++;
  state.lastStreakDate = todayISO();
  saveState(state);
}

/** Record hint usage for an exercise. */
export function recordHintUsed(state: GamificationState, exerciseId: string): void {
  state.hintsUsedPerExercise[exerciseId] = (state.hintsUsedPerExercise[exerciseId] || 0) + 1;
  saveState(state);
}

/** Check and unlock any new achievements. Returns newly unlocked ones. */
function checkAchievements(state: GamificationState): Achievement[] {
  const newlyUnlocked: Achievement[] = [];

  for (const achievement of ACHIEVEMENTS) {
    if (state.unlockedAchievements.includes(achievement.id)) continue;

    let earned = false;
    switch (achievement.id) {
      case "level_5":
        earned = getLevel(state.totalXP).rank >= 5;
        break;
      case "level_7":
        earned = getLevel(state.totalXP).rank >= 7;
        break;
      // Other achievements are unlocked externally via unlockAchievement()
    }

    if (earned) {
      state.unlockedAchievements.push(achievement.id);
      newlyUnlocked.push(achievement);
    }
  }

  return newlyUnlocked;
}

/** Manually unlock an achievement by ID. Returns the achievement if newly unlocked. */
export function unlockAchievement(
  state: GamificationState,
  achievementId: string
): Achievement | null {
  if (state.unlockedAchievements.includes(achievementId)) return null;
  const achievement = ACHIEVEMENTS.find((a) => a.id === achievementId);
  if (!achievement) return null;
  state.unlockedAchievements.push(achievementId);
  saveState(state);
  return achievement;
}

/**
 * Facts about a learner's progress that the count/threshold-based achievements
 * are derived from. Sourced from the progress backend + curriculum manifest,
 * NOT from gamification state — so reconciliation works even for learners whose
 * milestones predate an achievement being wired up.
 */
export interface ProgressFacts {
  lessonsCompleted: number;
  totalLessons: number;
  phasesCompleted: number;
  streakDays: number;
  /** Whether the learner has opened the projects page (persisted separately). */
  visitedProjects?: boolean;
}

/**
 * Unlock every threshold/count-based achievement the learner has already earned
 * but may be missing. Idempotent: `unlockAchievement` no-ops (and doesn't save)
 * for already-unlocked ids, so this is safe to call on every dashboard mount.
 *
 * This is the retroactive safety net for achievements that were either never
 * wired to a live event (e.g. "Halfway There", "Project Starter") or whose live
 * unlock is fragile (e.g. "Halfway Master" only fired during a phase-badge
 * celebration). Skill-based badges that can't be reconstructed from progress
 * alone (perfect_quiz, no_hints, speed_learner, first_quiz/exercise) stay on
 * their live unlock paths.
 */
export function reconcileAchievements(
  state: GamificationState,
  facts: ProgressFacts
): Achievement[] {
  const { lessonsCompleted, totalLessons, phasesCompleted, streakDays } = facts;
  const earned: string[] = [];

  if (lessonsCompleted >= 1) earned.push("first_lesson");
  if (lessonsCompleted >= 10) earned.push("ten_lessons");
  if (totalLessons > 0 && lessonsCompleted / totalLessons >= 0.5) earned.push("halfway");
  if (phasesCompleted >= 1) earned.push("phase_crusher");
  if (phasesCompleted >= 5) earned.push("five_phases");
  if (phasesCompleted >= 12) earned.push("full_stack");
  if (streakDays >= 3) earned.push("streak_3");
  if (streakDays >= 7) earned.push("streak_7");
  if (streakDays >= 14) earned.push("streak_14");
  if (streakDays >= 30) earned.push("streak_30");
  if (facts.visitedProjects) earned.push("project_starter");

  const rank = getLevel(state.totalXP).rank;
  if (rank >= 5) earned.push("level_5");
  if (rank >= 7) earned.push("level_7");

  const newly: Achievement[] = [];
  for (const id of earned) {
    const a = unlockAchievement(state, id);
    if (a) newly.push(a);
  }
  return newly;
}

/** Numeric progress toward a measurable achievement. */
export interface AchievementProgress {
  current: number;
  target: number;
  /** Short unit label for display, e.g. "lessons", "days", "XP". */
  unit: string;
}

/**
 * Progress toward a still-locked achievement, or null for binary/event badges
 * earned by a single action (first quiz, perfect score, no-hints pass, visiting
 * the projects page) where a progress bar would be meaningless. Powers the
 * "how do I earn this?" hints on the dashboard's locked badges.
 */
export function achievementProgress(
  id: string,
  facts: ProgressFacts,
  state: GamificationState
): AchievementProgress | null {
  const halfwayTarget =
    facts.totalLessons > 0 ? Math.ceil(facts.totalLessons / 2) : 0;
  const minXPForRank = (rank: number) =>
    LEVELS.find((l) => l.rank === rank)?.minXP ?? 0;
  const clamp = (current: number, target: number, unit: string) => ({
    current: Math.min(current, target),
    target,
    unit,
  });

  switch (id) {
    case "ten_lessons":
      return clamp(facts.lessonsCompleted, 10, "lessons");
    case "halfway":
      return halfwayTarget > 0
        ? clamp(facts.lessonsCompleted, halfwayTarget, "lessons")
        : null;
    case "phase_crusher":
      return clamp(facts.phasesCompleted, 1, "phases");
    case "five_phases":
      return clamp(facts.phasesCompleted, 5, "phases");
    case "full_stack":
      return clamp(facts.phasesCompleted, 12, "phases");
    case "streak_3":
      return clamp(facts.streakDays, 3, "days");
    case "streak_7":
      return clamp(facts.streakDays, 7, "days");
    case "streak_14":
      return clamp(facts.streakDays, 14, "days");
    case "streak_30":
      return clamp(facts.streakDays, 30, "days");
    case "level_5":
      return clamp(state.totalXP, minXPForRank(5), "XP");
    case "level_7":
      return clamp(state.totalXP, minXPForRank(7), "XP");
    default:
      // first_quiz, first_exercise, first_lesson, perfect_quiz, no_hints,
      // speed_learner, project_starter — single-action badges, no progress bar.
      return null;
  }
}

/** localStorage flag: has the learner ever opened the projects page? */
const PROJECTS_VISITED_KEY = "gamification:projects_visited";

export function markProjectsVisited(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(PROJECTS_VISITED_KEY, "1");
  } catch {
    // ignore
  }
}

export function hasVisitedProjects(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return localStorage.getItem(PROJECTS_VISITED_KEY) === "1";
  } catch {
    return false;
  }
}

/** Get streak fire level (0-4) for visual escalation. */
export function streakFireLevel(days: number): number {
  if (days >= 30) return 4;
  if (days >= 14) return 3;
  if (days >= 7) return 2;
  if (days >= 3) return 1;
  return 0;
}

/** Daily goal progress (0-100). Goal: complete 1 lesson per day. */
export function dailyGoalProgress(state: GamificationState): number {
  return Math.min(state.dailyLessonsCompleted * 100, 100);
}
