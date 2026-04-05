import { createBrowserClient as createBrowser } from "@supabase/ssr";
import { createClient } from "@supabase/supabase-js";

// Database types — matches platform/supabase/migrations/00001_initial_schema.sql
export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          username: string;
          display_name: string | null;
          avatar_url: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id: string;
          username: string;
          display_name?: string | null;
          avatar_url?: string | null;
        };
        Update: {
          username?: string;
          display_name?: string | null;
          avatar_url?: string | null;
          updated_at?: string;
        };
      };
      lesson_progress: {
        Row: {
          id: string;
          user_id: string;
          lesson_id: string;
          status: "not_started" | "in_progress" | "completed";
          started_at: string | null;
          completed_at: string | null;
          created_at: string;
        };
        Insert: {
          user_id: string;
          lesson_id: string;
          status?: "not_started" | "in_progress" | "completed";
          started_at?: string | null;
        };
        Update: {
          status?: "not_started" | "in_progress" | "completed";
          started_at?: string | null;
          completed_at?: string | null;
        };
      };
      submissions: {
        Row: {
          id: string;
          user_id: string;
          exercise_id: string;
          code: string;
          score: number | null;
          test_passed: boolean | null;
          test_results: unknown | null;
          rubric_score: number | null;
          rubric_feedback: string | null;
          submitted_at: string;
        };
        Insert: {
          user_id: string;
          exercise_id: string;
          code: string;
          score?: number | null;
          test_passed?: boolean | null;
          test_results?: unknown | null;
          rubric_score?: number | null;
          rubric_feedback?: string | null;
        };
        Update: {};
      };
      tutor_messages: {
        Row: {
          id: string;
          user_id: string;
          lesson_id: string;
          role: "user" | "assistant" | "system";
          content: string;
          created_at: string;
        };
        Insert: {
          user_id: string;
          lesson_id: string;
          role: "user" | "assistant" | "system";
          content: string;
        };
        Update: {};
      };
      quiz_results: {
        Row: {
          id: string;
          user_id: string;
          quiz_id: string;
          answers: unknown;
          score: number;
          completed_at: string;
        };
        Insert: {
          user_id: string;
          quiz_id: string;
          answers: unknown;
          score: number;
        };
        Update: {};
      };
      analytics_snapshots: {
        Row: {
          id: string;
          snapshot_date: string;
          phase_id: string;
          metrics: unknown;
        };
        Insert: {
          snapshot_date: string;
          phase_id: string;
          metrics: unknown;
        };
        Update: {};
      };
    };
  };
}

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

/**
 * Check if Supabase is configured with real credentials.
 * Returns false when using placeholder values from .env.example.
 */
export function isSupabaseConfigured(): boolean {
  if (!supabaseUrl || !supabaseAnonKey) return false;
  if (supabaseAnonKey === "your-anon-key") return false;
  if (supabaseAnonKey.length < 20) return false;
  return true;
}

/**
 * Create a Supabase client for use in browser/client components.
 * Returns null if Supabase is not configured.
 */
export function createBrowserClient() {
  if (!isSupabaseConfigured()) return null;
  return createBrowser<Database>(supabaseUrl, supabaseAnonKey);
}

/**
 * Create a Supabase client for use in server components and API routes.
 * Uses the service role key when available for elevated access.
 * Returns null if Supabase is not configured.
 */
export function createServerClient() {
  if (!isSupabaseConfigured()) return null;
  const serviceKey =
    process.env.SUPABASE_SERVICE_ROLE_KEY || supabaseAnonKey;

  return createClient<Database>(supabaseUrl, serviceKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}
