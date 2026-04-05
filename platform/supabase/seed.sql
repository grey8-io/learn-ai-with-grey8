-- =============================================================================
-- seed.sql — Local Development Seed Data
-- =============================================================================
-- WARNING: This file is for LOCAL DEVELOPMENT ONLY.
-- Never run this against a production database.
--
-- It inserts a test user profile so that the local dev environment has data
-- to work with immediately after `supabase db reset`.
--
-- The test user must first exist in auth.users (created via Supabase Auth
-- or the dashboard).  If using `supabase start`, you can sign up at
-- http://localhost:54323 (Studio) or via the Auth API.
-- =============================================================================

-- Insert a test profile.
-- The UUID below is a placeholder; replace it with the UUID from auth.users
-- after signing up your test user locally.
--
-- Example: after signing up test@example.com via the Auth API, query:
--   SELECT id FROM auth.users WHERE email = 'test@example.com';
-- Then replace the UUID below.

-- INSERT INTO profiles (id, username, display_name)
-- VALUES (
--     '00000000-0000-0000-0000-000000000001',
--     'testuser',
--     'Test Learner'
-- );

-- Uncomment the above once you have a matching auth.users row.

-- ---------------------------------------------------------------------------
-- Sample lesson progress (uncomment after creating the test profile)
-- ---------------------------------------------------------------------------
-- INSERT INTO lesson_progress (user_id, lesson_id, status, started_at)
-- VALUES (
--     '00000000-0000-0000-0000-000000000001',
--     'phase1/lesson01-hello-llm',
--     'in_progress',
--     now()
-- );

-- ---------------------------------------------------------------------------
-- Sample analytics snapshot
-- ---------------------------------------------------------------------------
INSERT INTO analytics_snapshots (snapshot_date, phase_id, metrics)
VALUES (
    CURRENT_DATE,
    'phase1',
    '{"total_users": 0, "lessons_completed": 0, "avg_score": 0}'::jsonb
);
