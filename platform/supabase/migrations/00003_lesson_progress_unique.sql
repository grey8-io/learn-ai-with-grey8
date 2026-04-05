-- =============================================================================
-- 00003_lesson_progress_unique.sql
-- =============================================================================
-- Add unique constraint on (user_id, lesson_id) to support upsert operations.
-- =============================================================================

ALTER TABLE lesson_progress
  ADD CONSTRAINT lesson_progress_user_lesson_unique UNIQUE (user_id, lesson_id);
