/**
 * Migrates progress data from localStorage to Supabase.
 * Called once when an anonymous user signs in or creates an account.
 */

import type { LocalStorageBackend } from "./local-backend";
import type { SupabaseBackend } from "./supabase-backend";

export interface MigrationResult {
  migrated: number;
  errors: string[];
}

export async function migrateLocalToSupabase(
  local: LocalStorageBackend,
  supabase: SupabaseBackend
): Promise<MigrationResult> {
  const result: MigrationResult = { migrated: 0, errors: [] };

  const data = local.exportAll();
  const hasData =
    data.lessons.length > 0 ||
    data.submissions.length > 0 ||
    data.quizzes.length > 0 ||
    Object.keys(data.chats).length > 0;

  if (!hasData) return result;

  // Migrate lesson progress
  for (const lesson of data.lessons) {
    try {
      if (lesson.status !== "not_started") {
        await supabase.upsertLessonProgress(lesson.lessonId, lesson.status);
        result.migrated++;
      }
    } catch (err) {
      result.errors.push(`lesson ${lesson.lessonId}: ${err}`);
    }
  }

  // Migrate submissions
  for (const sub of data.submissions) {
    try {
      await supabase.addSubmission(sub);
      result.migrated++;
    } catch (err) {
      result.errors.push(`submission ${sub.exerciseId}: ${err}`);
    }
  }

  // Migrate quiz results
  for (const quiz of data.quizzes) {
    try {
      await supabase.addQuizResult(quiz);
      result.migrated++;
    } catch (err) {
      result.errors.push(`quiz ${quiz.quizId}: ${err}`);
    }
  }

  // Migrate chat messages
  for (const [lessonId, messages] of Object.entries(data.chats)) {
    try {
      if (messages.length > 0) {
        await supabase.addChatMessages(messages);
        result.migrated += messages.length;
      }
    } catch (err) {
      result.errors.push(`chat ${lessonId}: ${err}`);
    }
  }

  // Clear localStorage after successful migration
  if (result.errors.length === 0) {
    local.clearAll();
  }

  return result;
}
