-- =============================================================================
-- 00001_initial_schema.sql
-- =============================================================================
-- Initial database schema for Learn AI With Grey8.
-- Creates core tables with Row-Level Security (RLS) policies.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Extensions
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------------------------
-- Custom types
-- ---------------------------------------------------------------------------
CREATE TYPE lesson_status AS ENUM ('not_started', 'in_progress', 'completed');

-- ---------------------------------------------------------------------------
-- Table: profiles
-- Extends Supabase auth.users with application-specific fields.
-- ---------------------------------------------------------------------------
CREATE TABLE profiles (
    id           UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username     TEXT UNIQUE NOT NULL,
    display_name TEXT,
    avatar_url   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE profiles IS 'Public user profiles linked to auth.users';

-- ---------------------------------------------------------------------------
-- Table: lesson_progress
-- Tracks each user''s progress through curriculum lessons.
-- ---------------------------------------------------------------------------
CREATE TABLE lesson_progress (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    lesson_id    TEXT NOT NULL,
    status       lesson_status NOT NULL DEFAULT 'not_started',
    started_at   TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (user_id, lesson_id)
);

COMMENT ON TABLE lesson_progress IS 'Per-user progress for each lesson';

-- ---------------------------------------------------------------------------
-- Table: submissions
-- Stores code exercise submissions with automated + rubric grading.
-- ---------------------------------------------------------------------------
CREATE TABLE submissions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    exercise_id     TEXT NOT NULL,
    code            TEXT NOT NULL,
    score           INTEGER,
    test_passed     BOOLEAN,
    test_results    JSONB,
    rubric_score    INTEGER,
    rubric_feedback TEXT,
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE submissions IS 'Code exercise submissions with grading results';

-- ---------------------------------------------------------------------------
-- Table: tutor_messages
-- Chat history between a user and the Socratic tutor per lesson.
-- ---------------------------------------------------------------------------
CREATE TABLE tutor_messages (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    lesson_id  TEXT NOT NULL,
    role       TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content    TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE tutor_messages IS 'Socratic tutor conversation history';

-- ---------------------------------------------------------------------------
-- Table: quiz_results
-- Stores quiz attempts and scores.
-- ---------------------------------------------------------------------------
CREATE TABLE quiz_results (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    quiz_id      TEXT NOT NULL,
    answers      JSONB NOT NULL,
    score        INTEGER NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE quiz_results IS 'Quiz attempt results';

-- ---------------------------------------------------------------------------
-- Table: analytics_snapshots
-- Daily aggregate metrics per curriculum phase (for dashboards).
-- ---------------------------------------------------------------------------
CREATE TABLE analytics_snapshots (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    snapshot_date DATE NOT NULL,
    phase_id      TEXT NOT NULL,
    metrics       JSONB NOT NULL,

    UNIQUE (snapshot_date, phase_id)
);

COMMENT ON TABLE analytics_snapshots IS 'Daily aggregate analytics per phase';

-- =============================================================================
-- Row-Level Security (RLS)
-- =============================================================================

ALTER TABLE profiles           ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson_progress    ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions        ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor_messages     ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_results       ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_snapshots ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- Policies: profiles
-- ---------------------------------------------------------------------------
CREATE POLICY "Users can view their own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ---------------------------------------------------------------------------
-- Policies: lesson_progress
-- ---------------------------------------------------------------------------
CREATE POLICY "Users can view their own lesson progress"
    ON lesson_progress FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own lesson progress"
    ON lesson_progress FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own lesson progress"
    ON lesson_progress FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- Policies: submissions
-- ---------------------------------------------------------------------------
CREATE POLICY "Users can view their own submissions"
    ON submissions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own submissions"
    ON submissions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- Policies: tutor_messages
-- ---------------------------------------------------------------------------
CREATE POLICY "Users can view their own tutor messages"
    ON tutor_messages FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own tutor messages"
    ON tutor_messages FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- Policies: quiz_results
-- ---------------------------------------------------------------------------
CREATE POLICY "Users can view their own quiz results"
    ON quiz_results FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own quiz results"
    ON quiz_results FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- Policies: analytics_snapshots (readable by all authenticated users)
-- ---------------------------------------------------------------------------
CREATE POLICY "Authenticated users can view analytics"
    ON analytics_snapshots FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Only service role can insert analytics"
    ON analytics_snapshots FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

-- =============================================================================
-- Indexes
-- =============================================================================

CREATE INDEX idx_lesson_progress_user_id   ON lesson_progress(user_id);
CREATE INDEX idx_lesson_progress_lesson_id ON lesson_progress(lesson_id);
CREATE INDEX idx_submissions_user_id       ON submissions(user_id);
CREATE INDEX idx_submissions_exercise_id   ON submissions(exercise_id);
CREATE INDEX idx_tutor_messages_user_id    ON tutor_messages(user_id);
CREATE INDEX idx_tutor_messages_lesson_id  ON tutor_messages(lesson_id);
CREATE INDEX idx_quiz_results_user_id      ON quiz_results(user_id);
CREATE INDEX idx_quiz_results_quiz_id      ON quiz_results(quiz_id);
CREATE INDEX idx_analytics_phase_id        ON analytics_snapshots(phase_id);
CREATE INDEX idx_analytics_snapshot_date   ON analytics_snapshots(snapshot_date);

-- ---------------------------------------------------------------------------
-- Trigger: auto-update updated_at on profiles
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
