/**
 * Supabase-based progress backend.
 * Used for authenticated users when Supabase is configured.
 * Data persists in Postgres with row-level security.
 */

import type { SupabaseClient } from "@supabase/supabase-js";
import type {
  ProgressBackend,
  LessonStatus,
  Submission,
  QuizResult,
  ChatMessage,
  ProgressStats,
} from "./types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export class SupabaseBackend implements ProgressBackend {
  constructor(
    private supabase: SupabaseClient<any>,
    private userId: string
  ) {}

  // -- Lessons ---------------------------------------------------------------

  async getLessonProgress(lessonId: string): Promise<LessonStatus | null> {
    const { data } = await this.supabase
      .from("lesson_progress")
      .select("lesson_id, status, started_at, completed_at")
      .eq("user_id", this.userId)
      .eq("lesson_id", lessonId)
      .single();

    if (!data) return null;
    return {
      lessonId: data.lesson_id,
      status: data.status,
      startedAt: data.started_at ?? undefined,
      completedAt: data.completed_at ?? undefined,
    };
  }

  async getAllLessonProgress(): Promise<LessonStatus[]> {
    const { data } = await this.supabase
      .from("lesson_progress")
      .select("lesson_id, status, started_at, completed_at")
      .eq("user_id", this.userId);

    return (data ?? []).map((row) => ({
      lessonId: row.lesson_id,
      status: row.status,
      startedAt: row.started_at ?? undefined,
      completedAt: row.completed_at ?? undefined,
    }));
  }

  async upsertLessonProgress(
    lessonId: string,
    status: "in_progress" | "completed"
  ): Promise<void> {
    const now = new Date().toISOString();

    // Check if we already have a completed status — don't downgrade
    const existing = await this.getLessonProgress(lessonId);
    if (existing?.status === "completed" && status === "in_progress") return;

    await this.supabase.from("lesson_progress").upsert(
      {
        user_id: this.userId,
        lesson_id: lessonId,
        status,
        started_at: existing?.startedAt ?? now,
        completed_at: status === "completed" ? now : null,
      },
      { onConflict: "user_id,lesson_id" }
    );
  }

  // -- Submissions -----------------------------------------------------------

  async addSubmission(submission: Submission): Promise<void> {
    await this.supabase.from("submissions").insert({
      user_id: this.userId,
      exercise_id: submission.exerciseId,
      code: submission.code,
      score: submission.score,
      test_passed: submission.testPassed,
      test_results: submission.testResults,
      rubric_score: submission.rubricScore,
      rubric_feedback: submission.rubricFeedback,
    });
  }

  async getSubmissions(exerciseId: string): Promise<Submission[]> {
    const { data } = await this.supabase
      .from("submissions")
      .select("*")
      .eq("user_id", this.userId)
      .eq("exercise_id", exerciseId)
      .order("submitted_at", { ascending: false });

    return (data ?? []).map((row) => ({
      exerciseId: row.exercise_id,
      code: row.code,
      score: row.score,
      testPassed: row.test_passed,
      testResults: row.test_results,
      rubricScore: row.rubric_score,
      rubricFeedback: row.rubric_feedback,
      submittedAt: row.submitted_at,
    }));
  }

  async getBestSubmission(exerciseId: string): Promise<Submission | null> {
    const { data } = await this.supabase
      .from("submissions")
      .select("*")
      .eq("user_id", this.userId)
      .eq("exercise_id", exerciseId)
      .order("score", { ascending: false })
      .limit(1)
      .single();

    if (!data) return null;
    return {
      exerciseId: data.exercise_id,
      code: data.code,
      score: data.score,
      testPassed: data.test_passed,
      testResults: data.test_results,
      rubricScore: data.rubric_score,
      rubricFeedback: data.rubric_feedback,
      submittedAt: data.submitted_at,
    };
  }

  // -- Quizzes ---------------------------------------------------------------

  async addQuizResult(result: QuizResult): Promise<void> {
    await this.supabase.from("quiz_results").insert({
      user_id: this.userId,
      quiz_id: result.quizId,
      answers: result.answers,
      score: result.score,
    });
  }

  async getQuizResult(quizId: string): Promise<QuizResult | null> {
    const { data } = await this.supabase
      .from("quiz_results")
      .select("*")
      .eq("user_id", this.userId)
      .eq("quiz_id", quizId)
      .order("score", { ascending: false })
      .limit(1)
      .single();

    if (!data) return null;
    return {
      quizId: data.quiz_id,
      answers: data.answers as QuizResult["answers"],
      score: data.score,
      completedAt: data.completed_at,
    };
  }

  // -- Chat ------------------------------------------------------------------

  async getChatMessages(lessonId: string): Promise<ChatMessage[]> {
    const { data } = await this.supabase
      .from("tutor_messages")
      .select("lesson_id, role, content, created_at")
      .eq("user_id", this.userId)
      .eq("lesson_id", lessonId)
      .order("created_at", { ascending: true });

    return (data ?? [])
      .filter((row) => row.role === "user" || row.role === "assistant")
      .map((row) => ({
        lessonId: row.lesson_id,
        role: row.role as "user" | "assistant",
        content: row.content,
        createdAt: row.created_at,
      }));
  }

  async addChatMessages(messages: ChatMessage[]): Promise<void> {
    if (messages.length === 0) return;
    await this.supabase.from("tutor_messages").insert(
      messages.map((m) => ({
        user_id: this.userId,
        lesson_id: m.lessonId,
        role: m.role,
        content: m.content,
      }))
    );
  }

  async clearChatMessages(lessonId: string): Promise<void> {
    await this.supabase
      .from("tutor_messages")
      .delete()
      .eq("user_id", this.userId)
      .eq("lesson_id", lessonId);
  }

  // -- Stats -----------------------------------------------------------------

  async getStats(): Promise<ProgressStats> {
    const [lessons, submissions, quizzes] = await Promise.all([
      this.getAllLessonProgress(),
      this.supabase
        .from("submissions")
        .select("exercise_id, score, submitted_at")
        .eq("user_id", this.userId),
      this.supabase
        .from("quiz_results")
        .select("quiz_id, score, completed_at")
        .eq("user_id", this.userId),
    ]);

    const subs = submissions.data ?? [];
    const qzs = quizzes.data ?? [];

    // Collect timestamps for streak
    const timestamps: string[] = [];
    for (const l of lessons) {
      if (l.startedAt) timestamps.push(l.startedAt);
      if (l.completedAt) timestamps.push(l.completedAt);
    }
    for (const s of subs) timestamps.push(s.submitted_at);
    for (const q of qzs) timestamps.push(q.completed_at);

    // Best per exercise
    const bestByExercise = new Map<string, number>();
    for (const s of subs) {
      const current = bestByExercise.get(s.exercise_id) ?? 0;
      if ((s.score ?? 0) > current) {
        bestByExercise.set(s.exercise_id, s.score ?? 0);
      }
    }
    const exercisesPassed = [...bestByExercise.values()].filter(
      (score) => score >= 70
    ).length;

    // Unique quizzes
    const uniqueQuizIds = new Set(qzs.map((q) => q.quiz_id));

    // Streak
    const streak = computeStreak(timestamps);

    return {
      lessonsCompleted: lessons.filter((l) => l.status === "completed").length,
      lessonsInProgress: lessons.filter((l) => l.status === "in_progress")
        .length,
      exercisesPassed,
      totalSubmissions: subs.length,
      quizzesCompleted: uniqueQuizIds.size,
      currentStreakDays: streak,
      lastActiveDate:
        timestamps.length > 0 ? timestamps.sort().reverse()[0] : null,
    };
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
  const d = new Date(today);

  for (let i = 0; i < 365; i++) {
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    if (days.has(key)) {
      streak++;
    } else if (i > 0) {
      break;
    }
    d.setDate(d.getDate() - 1);
  }

  return streak;
}
