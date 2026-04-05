/**
 * localStorage-based progress backend.
 * Used for anonymous users or when Supabase is not configured.
 * Persists across page refreshes and service restarts.
 */

import type {
  ProgressBackend,
  LessonStatus,
  Submission,
  QuizResult,
  ChatMessage,
  ProgressStats,
  ExportedData,
} from "./types";

const KEYS = {
  lessons: "progress:lessons",
  submissions: "progress:submissions",
  quizzes: "progress:quizzes",
  chatPrefix: "progress:chat:",
} as const;

function isClient(): boolean {
  return typeof window !== "undefined";
}

function read<T>(key: string, fallback: T): T {
  if (!isClient()) return fallback;
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function write<T>(key: string, value: T): void {
  if (!isClient()) return;
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // localStorage full or blocked — silently ignore
  }
}

function computeStreak(timestamps: string[]): number {
  if (timestamps.length === 0) return 0;

  const days = new Set(
    timestamps.map((ts) => {
      const d = new Date(ts);
      return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    })
  );

  const today = new Date();
  let streak = 0;
  let d = new Date(today);

  // Check today first, then walk backwards
  for (let i = 0; i < 365; i++) {
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    if (days.has(key)) {
      streak++;
    } else if (i > 0) {
      // Allow skipping today (streak counts if yesterday was active)
      break;
    }
    d.setDate(d.getDate() - 1);
  }

  return streak;
}

export class LocalStorageBackend implements ProgressBackend {
  // -- Lessons ---------------------------------------------------------------

  async getLessonProgress(lessonId: string): Promise<LessonStatus | null> {
    const all = read<LessonStatus[]>(KEYS.lessons, []);
    return all.find((l) => l.lessonId === lessonId) ?? null;
  }

  async getAllLessonProgress(): Promise<LessonStatus[]> {
    return read<LessonStatus[]>(KEYS.lessons, []);
  }

  async upsertLessonProgress(
    lessonId: string,
    status: "in_progress" | "completed"
  ): Promise<void> {
    const all = read<LessonStatus[]>(KEYS.lessons, []);
    const existing = all.find((l) => l.lessonId === lessonId);
    const now = new Date().toISOString();

    if (existing) {
      // Don't downgrade from completed to in_progress
      if (existing.status === "completed" && status === "in_progress") return;
      existing.status = status;
      if (status === "completed") existing.completedAt = now;
    } else {
      all.push({
        lessonId,
        status,
        startedAt: now,
        completedAt: status === "completed" ? now : undefined,
      });
    }

    write(KEYS.lessons, all);
  }

  // -- Submissions -----------------------------------------------------------

  async addSubmission(submission: Submission): Promise<void> {
    const all = read<Submission[]>(KEYS.submissions, []);
    all.push(submission);
    write(KEYS.submissions, all);
  }

  async getSubmissions(exerciseId: string): Promise<Submission[]> {
    const all = read<Submission[]>(KEYS.submissions, []);
    return all.filter((s) => s.exerciseId === exerciseId);
  }

  async getBestSubmission(exerciseId: string): Promise<Submission | null> {
    const subs = await this.getSubmissions(exerciseId);
    if (subs.length === 0) return null;
    return subs.reduce((best, s) =>
      (s.score ?? 0) > (best.score ?? 0) ? s : best
    );
  }

  // -- Quizzes ---------------------------------------------------------------

  async addQuizResult(result: QuizResult): Promise<void> {
    const all = read<QuizResult[]>(KEYS.quizzes, []);
    // Keep best attempt per quiz
    const idx = all.findIndex((q) => q.quizId === result.quizId);
    if (idx >= 0 && all[idx].score >= result.score) {
      // Already have a better score
      return;
    }
    if (idx >= 0) {
      all[idx] = result;
    } else {
      all.push(result);
    }
    write(KEYS.quizzes, all);
  }

  async getQuizResult(quizId: string): Promise<QuizResult | null> {
    const all = read<QuizResult[]>(KEYS.quizzes, []);
    return all.find((q) => q.quizId === quizId) ?? null;
  }

  // -- Chat ------------------------------------------------------------------

  async getChatMessages(lessonId: string): Promise<ChatMessage[]> {
    return read<ChatMessage[]>(`${KEYS.chatPrefix}${lessonId}`, []);
  }

  async addChatMessages(messages: ChatMessage[]): Promise<void> {
    if (messages.length === 0) return;
    const lessonId = messages[0].lessonId;
    const existing = read<ChatMessage[]>(
      `${KEYS.chatPrefix}${lessonId}`,
      []
    );
    existing.push(...messages);
    write(`${KEYS.chatPrefix}${lessonId}`, existing);
  }

  async clearChatMessages(lessonId: string): Promise<void> {
    if (!isClient()) return;
    localStorage.removeItem(`${KEYS.chatPrefix}${lessonId}`);
  }

  // -- Stats -----------------------------------------------------------------

  async getStats(): Promise<ProgressStats> {
    const lessons = read<LessonStatus[]>(KEYS.lessons, []);
    const submissions = read<Submission[]>(KEYS.submissions, []);
    const quizzes = read<QuizResult[]>(KEYS.quizzes, []);

    // Collect all timestamps for streak calculation
    const timestamps: string[] = [];
    for (const l of lessons) {
      if (l.startedAt) timestamps.push(l.startedAt);
      if (l.completedAt) timestamps.push(l.completedAt);
    }
    for (const s of submissions) timestamps.push(s.submittedAt);
    for (const q of quizzes) timestamps.push(q.completedAt);

    // Count exercises that passed (best submission per exercise)
    const bestByExercise = new Map<string, number>();
    for (const s of submissions) {
      const current = bestByExercise.get(s.exerciseId) ?? 0;
      if ((s.score ?? 0) > current) {
        bestByExercise.set(s.exerciseId, s.score ?? 0);
      }
    }
    const exercisesPassed = [...bestByExercise.values()].filter(
      (score) => score >= 70
    ).length;

    return {
      lessonsCompleted: lessons.filter((l) => l.status === "completed").length,
      lessonsInProgress: lessons.filter((l) => l.status === "in_progress")
        .length,
      exercisesPassed,
      totalSubmissions: submissions.length,
      quizzesCompleted: quizzes.length,
      currentStreakDays: computeStreak(timestamps),
      lastActiveDate:
        timestamps.length > 0
          ? timestamps.sort().reverse()[0]
          : null,
    };
  }

  // -- Migration support -----------------------------------------------------

  exportAll(): ExportedData {
    const lessons = read<LessonStatus[]>(KEYS.lessons, []);
    const submissions = read<Submission[]>(KEYS.submissions, []);
    const quizzes = read<QuizResult[]>(KEYS.quizzes, []);

    // Collect all chat keys
    const chats: Record<string, ChatMessage[]> = {};
    if (isClient()) {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(KEYS.chatPrefix)) {
          const lessonId = key.slice(KEYS.chatPrefix.length);
          chats[lessonId] = read<ChatMessage[]>(key, []);
        }
      }
    }

    return { lessons, submissions, quizzes, chats };
  }

  clearAll(): void {
    if (!isClient()) return;
    const keysToRemove: string[] = [
      KEYS.lessons,
      KEYS.submissions,
      KEYS.quizzes,
    ];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(KEYS.chatPrefix)) {
        keysToRemove.push(key);
      }
    }
    for (const key of keysToRemove) {
      localStorage.removeItem(key);
    }
  }
}
