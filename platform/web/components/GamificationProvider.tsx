"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from "react";
import Confetti from "./Confetti";
import GamificationToast, { type ToastData } from "./GamificationToast";
import {
  type GamificationState,
  type GamificationResult,
  type Achievement,
  type ProgressFacts,
  defaultState,
  loadState,
  saveState,
  awardXP,
  recordDailyLesson,
  recordHintUsed,
  unlockAchievement,
  reconcileAchievements,
  getLevel,
  getNextLevel,
  getLevelProgress,
  streakFireLevel,
  dailyGoalProgress,
  quizXP,
  exerciseXP,
  lessonCompleteXP,
} from "@/lib/gamification";

interface GamificationContextValue {
  state: GamificationState;
  /** Award XP for a quiz score. */
  onQuizComplete: (score: number, total: number, streakDays: number) => GamificationResult;
  /** Award XP for an exercise score. Pass exerciseId to credit "No Hints Needed". */
  onExerciseComplete: (score: number, streakDays: number, exerciseId?: string) => GamificationResult;
  /** Award XP for lesson completion. */
  onLessonComplete: (streakDays: number) => GamificationResult;
  /** Record a hint used (for "No Hints" achievement tracking). */
  onHintUsed: (exerciseId: string) => void;
  /** Manually unlock an achievement. */
  unlock: (achievementId: string) => void;
  /** Retroactively unlock any progress-derived achievements already earned. */
  reconcile: (facts: ProgressFacts) => void;
  /** Trigger confetti. */
  celebrate: () => void;
  /** XP, level, and progress helpers. */
  totalXP: number;
  level: ReturnType<typeof getLevel>;
  nextLevel: ReturnType<typeof getNextLevel>;
  levelProgress: number;
  fireLevel: number;
  dailyProgress: number;
}

const GamificationContext = createContext<GamificationContextValue | null>(null);

export function useGamification() {
  const ctx = useContext(GamificationContext);
  if (!ctx) throw new Error("useGamification must be used within GamificationProvider");
  return ctx;
}

export default function GamificationProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<GamificationState>(defaultState);
  const [toasts, setToasts] = useState<ToastData[]>([]);
  const [confettiActive, setConfettiActive] = useState(false);
  const [streakDaysCache, setStreakDaysCache] = useState(0);

  // Keep in-memory state in sync with localStorage.
  // - on mount: load persisted state
  // - on `storage`: another tab wrote new state (cross-tab sync)
  // - on focus/visibility: re-run loadState() so the daily-goal reset fires
  //   when the calendar date has rolled over while the tab sat idle.
  // All mutations call saveState() synchronously, so localStorage is always
  // the source of truth — re-reading it never clobbers unsaved work.
  useEffect(() => {
    const sync = () => setState(loadState());
    sync();
    const onVisible = () => {
      if (document.visibilityState === "visible") sync();
    };
    window.addEventListener("storage", sync);
    window.addEventListener("focus", sync);
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      window.removeEventListener("storage", sync);
      window.removeEventListener("focus", sync);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, []);

  const addToast = useCallback((toast: Omit<ToastData, "id">) => {
    const id = Math.random().toString(36).slice(2, 9);
    setToasts((prev) => [...prev, { ...toast, id }]);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toastAchievement = useCallback(
    (a: Achievement) => {
      addToast({
        type: "achievement",
        title: `${a.icon} ${a.title}`,
        subtitle: a.description,
        icon: "🏅",
      });
    },
    [addToast]
  );

  const celebrate = useCallback(() => {
    setConfettiActive(true);
    setTimeout(() => setConfettiActive(false), 100); // Confetti component handles duration
  }, []);

  const showResult = useCallback(
    (result: GamificationResult) => {
      if (result.xpGained > 0) {
        addToast({
          type: "xp",
          title: `+${result.xpGained} XP`,
          subtitle: state.totalXP >= 0 ? `Total: ${state.totalXP} XP` : undefined,
          icon: "✨",
        });
      }
      if (result.leveledUp) {
        addToast({
          type: "level_up",
          title: `Level Up! ${result.newLevel.icon} ${result.newLevel.title}`,
          subtitle: `You're now Level ${result.newLevel.rank}`,
          icon: "🎉",
        });
        celebrate();
      }
      for (const a of result.newAchievements) {
        addToast({
          type: "achievement",
          title: `${a.icon} ${a.title}`,
          subtitle: a.description,
          icon: "🏅",
        });
      }
    },
    [addToast, celebrate, state.totalXP]
  );

  const onQuizComplete = useCallback(
    (score: number, total: number, streakDays: number) => {
      setStreakDaysCache(streakDays);
      const xp = quizXP(score, total, streakDays);
      const result = awardXP(state, xp, `Quiz: ${score}/${total}`);
      // Check quiz-specific achievements
      if (score === total) unlockAchievement(state, "perfect_quiz");
      unlockAchievement(state, "first_quiz");
      setState({ ...state });
      showResult(result);
      return result;
    },
    [state, showResult]
  );

  const onExerciseComplete = useCallback(
    (score: number, streakDays: number, exerciseId?: string) => {
      setStreakDaysCache(streakDays);
      const xp = exerciseXP(score, streakDays);
      const result = awardXP(state, xp, `Exercise: ${score}%`);
      unlockAchievement(state, "first_exercise");
      // "No Hints Needed": passed this exercise without ever requesting a hint.
      if (exerciseId && (state.hintsUsedPerExercise[exerciseId] ?? 0) === 0) {
        const a = unlockAchievement(state, "no_hints");
        if (a) toastAchievement(a);
      }
      setState({ ...state });
      showResult(result);
      return result;
    },
    [state, showResult, toastAchievement]
  );

  const onLessonComplete = useCallback(
    (streakDays: number) => {
      setStreakDaysCache(streakDays);
      const xp = lessonCompleteXP(streakDays);
      const result = awardXP(state, xp, "Lesson completed");
      recordDailyLesson(state);
      unlockAchievement(state, "first_lesson");
      // Check milestone achievements. The xpLog only retains the last 20 events,
      // so this can undercount past 10 lessons — the dashboard reconcile pass
      // (reconcileAchievements, sourced from the progress backend) is the
      // authoritative backstop. This live check just catches the common case.
      const completed = state.xpLog.filter((e) => e.reason === "Lesson completed").length;
      if (completed >= 10) unlockAchievement(state, "ten_lessons");
      // "Speed Learner": 3 lessons completed within the same calendar day.
      if (state.dailyLessonsCompleted >= 3) {
        const a = unlockAchievement(state, "speed_learner");
        if (a) toastAchievement(a);
      }
      // Streak achievements
      if (streakDays >= 3) unlockAchievement(state, "streak_3");
      if (streakDays >= 7) unlockAchievement(state, "streak_7");
      if (streakDays >= 14) unlockAchievement(state, "streak_14");
      if (streakDays >= 30) unlockAchievement(state, "streak_30");
      setState({ ...state });
      showResult(result);
      celebrate();
      return result;
    },
    [state, showResult, celebrate, toastAchievement]
  );

  const onHintUsed = useCallback(
    (exerciseId: string) => {
      recordHintUsed(state, exerciseId);
      setState({ ...state });
    },
    [state]
  );

  const unlock = useCallback(
    (achievementId: string) => {
      const a = unlockAchievement(state, achievementId);
      if (a) {
        toastAchievement(a);
        setState({ ...state });
      }
    },
    [state, toastAchievement]
  );

  const reconcile = useCallback(
    (facts: ProgressFacts) => {
      const newly = reconcileAchievements(state, facts);
      if (newly.length > 0) {
        newly.forEach(toastAchievement);
        setState({ ...state });
      }
    },
    [state, toastAchievement]
  );

  const value: GamificationContextValue = {
    state,
    onQuizComplete,
    onExerciseComplete,
    onLessonComplete,
    onHintUsed,
    unlock,
    reconcile,
    celebrate,
    totalXP: state.totalXP,
    level: getLevel(state.totalXP),
    nextLevel: getNextLevel(state.totalXP),
    levelProgress: getLevelProgress(state.totalXP),
    fireLevel: streakFireLevel(streakDaysCache),
    dailyProgress: dailyGoalProgress(state),
  };

  return (
    <GamificationContext.Provider value={value}>
      {children}
      <Confetti active={confettiActive} />
      <GamificationToast toasts={toasts} onDismiss={dismissToast} />
    </GamificationContext.Provider>
  );
}
