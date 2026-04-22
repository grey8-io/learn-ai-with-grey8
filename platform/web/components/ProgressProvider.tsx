"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { useAuth } from "@/components/AuthProvider";
import { createBrowserClient } from "@/lib/supabase";
import type { ProgressBackend, ProgressStats } from "@/lib/progress";
import {
  LocalStorageBackend,
  SupabaseBackend,
  migrateLocalToSupabase,
} from "@/lib/progress";

interface ProgressContextType {
  backend: ProgressBackend;
  stats: ProgressStats | null;
  refreshStats: () => Promise<void>;
  isReady: boolean;
}

const defaultStats: ProgressStats = {
  lessonsCompleted: 0,
  lessonsInProgress: 0,
  exercisesPassed: 0,
  totalSubmissions: 0,
  quizzesCompleted: 0,
  currentStreakDays: 0,
  lastActiveDate: null,
};

const localBackendSingleton = new LocalStorageBackend();

const ProgressContext = createContext<ProgressContextType>({
  backend: localBackendSingleton,
  stats: null,
  refreshStats: async () => {},
  isReady: false,
});

export function ProgressProvider({ children }: { children: ReactNode }) {
  const { user, loading: authLoading } = useAuth();
  const [stats, setStats] = useState<ProgressStats | null>(null);
  const [isReady, setIsReady] = useState(false);
  const prevUserRef = useRef<string | null>(null);

  // Select backend based on auth state
  const backend = useMemo<ProgressBackend>(() => {
    if (!user) return localBackendSingleton;

    const supabase = createBrowserClient();
    if (!supabase) return localBackendSingleton;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return new SupabaseBackend(supabase as any, user.id);
  }, [user]);

  const refreshStats = useCallback(async () => {
    try {
      const s = await backend.getStats();
      // Bail out if the new stats are structurally identical to the previous
      // snapshot. Without this, getStats() returns a fresh object each call,
      // so setStats(s) triggers a cascade of re-renders in consumers that
      // have `stats` in a useCallback/useMemo dep list — which ends up
      // re-running lesson/exercise page useEffects in a loop.
      setStats(prev => {
        if (prev && JSON.stringify(prev) === JSON.stringify(s)) return prev;
        return s;
      });
    } catch {
      setStats(prev => prev ?? defaultStats);
    }
  }, [backend]);

  // Migration: when user transitions from null to signed-in
  useEffect(() => {
    if (authLoading) return;

    const currentUserId = user?.id ?? null;
    const prevUserId = prevUserRef.current;

    // Detect transition from anonymous to authenticated
    if (prevUserId === null && currentUserId !== null) {
      const supabase = createBrowserClient();
      if (supabase) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const supabaseBackend = new SupabaseBackend(supabase as any, currentUserId);
        migrateLocalToSupabase(localBackendSingleton, supabaseBackend)
          .then((result) => {
            if (result.migrated > 0) {
              console.log(
                `Migrated ${result.migrated} progress records to your account`
              );
            }
            if (result.errors.length > 0) {
              console.warn("Migration errors:", result.errors);
            }
          })
          .catch((err) => console.error("Migration failed:", err))
          .finally(() => refreshStats());
      }
    }

    prevUserRef.current = currentUserId;
  }, [user, authLoading, refreshStats]);

  // Load stats when backend changes or on mount
  useEffect(() => {
    if (authLoading) return;

    setIsReady(false);
    refreshStats().finally(() => setIsReady(true));
  }, [backend, authLoading, refreshStats]);

  return (
    <ProgressContext.Provider value={{ backend, stats, refreshStats, isReady }}>
      {children}
    </ProgressContext.Provider>
  );
}

export function useProgress() {
  return useContext(ProgressContext);
}
