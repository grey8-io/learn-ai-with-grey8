"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useProgress } from "@/components/ProgressProvider";
import { useAuth } from "@/components/AuthProvider";
import { useGamification } from "@/components/GamificationProvider";
import { fetchManifest } from "@/lib/api";
import { ACHIEVEMENTS, streakFireLevel } from "@/lib/gamification";

const STREAK_FIRES = ["", "🔥", "🔥🔥", "🔥🔥🔥", "🔥🔥🔥🔥"];
const STREAK_LABELS = ["Start today!", "Warming up!", "On fire!", "Unstoppable!", "LEGENDARY!"];

export default function DashboardPage() {
  const { stats, isReady } = useProgress();
  const { user, isConfigured: authConfigured } = useAuth();
  const { totalXP, level, nextLevel, levelProgress, state, dailyProgress } = useGamification();
  const [totalLessons, setTotalLessons] = useState(0);

  useEffect(() => {
    fetchManifest()
      .then((m) => {
        const count = m.phases.reduce(
          (sum: number, p: { lessons: unknown[] }) => sum + p.lessons.length,
          0
        );
        setTotalLessons(count);
      })
      .catch(() => {});
  }, []);

  const lessonsCompleted = stats?.lessonsCompleted ?? 0;
  const streakDays = stats?.currentStreakDays ?? 0;
  const fireLevel = streakFireLevel(streakDays);
  const unlockedCount = state.unlockedAchievements.length;

  return (
    <div className="space-y-10">
      {/* Hero section */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-900/80 via-primary-800/60 to-surface-800 p-8 sm:p-12">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDE0djJoLTJ2LTJoMnptMCAyMHYyaC0ydi0yaDJ6bS0yMC0yMHYyaC0ydi0yaDJ6bTAgMjB2MmgtMnYtMmgyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-50" />
        <div className="relative flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl lg:text-5xl">
              Welcome to{" "}
              <span className="bg-gradient-to-r from-primary-300 to-primary-100 bg-clip-text text-transparent">
                Learn AI With Grey8
              </span>
            </h1>
            <p className="mt-4 max-w-2xl text-lg text-slate-300">
              Your self-driving AI tutor guides you through 15 hands-on projects.
              Learn at your own pace with personalized feedback.
            </p>
            <div className="mt-6 flex flex-wrap gap-4">
              <Link href="/learn/phases" className="btn-primary text-base px-6 py-3">
                Start Learning
              </Link>
              <Link href="/projects" className="btn-secondary text-base px-6 py-3">
                View Projects
              </Link>
            </div>
          </div>

          {/* Level badge (hero right side) */}
          <div className="flex flex-col items-center shrink-0">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20 text-4xl shadow-xl">
              {level.icon}
            </div>
            <p className="mt-2 text-lg font-bold text-white">{level.title}</p>
            <p className="text-sm text-primary-300">{totalXP.toLocaleString()} XP</p>
          </div>
        </div>
      </section>

      {/* Sign-in prompt */}
      {!user && isReady && authConfigured && (
        <div className="flex items-center gap-3 rounded-xl border border-primary-500/20 bg-primary-600/5 p-4">
          <svg className="h-5 w-5 shrink-0 text-primary-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
          </svg>
          <p className="text-sm text-slate-300">
            Your progress is saved locally.{" "}
            <Link href="/auth/register" className="font-medium text-primary-400 hover:text-primary-300">
              Create an account
            </Link>{" "}
            to sync across devices.
          </p>
        </div>
      )}

      {/* XP Bar + Daily Goal + Streak — top gamification row */}
      <section className="grid gap-4 sm:grid-cols-3">
        {/* XP Progress */}
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-300">
              {level.icon} Level {level.rank}: {level.title}
            </span>
            {nextLevel && (
              <span className="text-xs text-slate-500">
                {nextLevel.minXP - totalXP} XP to {nextLevel.title}
              </span>
            )}
          </div>
          <div className="h-3 w-full rounded-full bg-slate-700 overflow-hidden">
            <div
              className="h-3 rounded-full bg-gradient-to-r from-primary-600 to-primary-400 transition-all duration-500"
              style={{ width: `${levelProgress}%` }}
            />
          </div>
          <p className="mt-2 text-2xl font-bold text-primary-400">
            {totalXP.toLocaleString()} <span className="text-sm font-normal text-slate-500">XP</span>
          </p>
        </div>

        {/* Daily Goal Ring */}
        <div className="card flex items-center gap-5">
          <div className="relative h-16 w-16 shrink-0">
            <svg className="h-16 w-16 -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" stroke="#334155" strokeWidth="8" />
              <circle
                cx="50" cy="50" r="45" fill="none"
                stroke={dailyProgress >= 100 ? "#34d399" : "#818cf8"}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray="283"
                strokeDashoffset={283 - (283 * Math.min(dailyProgress, 100)) / 100}
                className="animate-goal-fill transition-all duration-500"
              />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-lg font-bold text-white">
              {dailyProgress >= 100 ? "✓" : `${state.dailyLessonsCompleted}`}
            </span>
          </div>
          <div>
            <p className="text-sm font-medium text-slate-300">Daily Goal</p>
            <p className="text-xs text-slate-500">
              {dailyProgress >= 100
                ? "Goal reached! Keep going!"
                : "Complete 1 lesson today"}
            </p>
          </div>
        </div>

        {/* Streak */}
        <div className="card flex items-center gap-5">
          <div className={`text-4xl ${fireLevel >= 2 ? "animate-fire-pulse" : ""}`}>
            {streakDays > 0 ? STREAK_FIRES[fireLevel] || "🔥" : "❄️"}
          </div>
          <div>
            <p className="text-2xl font-bold text-rose-400">
              {streakDays} <span className="text-sm font-normal text-slate-500">day{streakDays !== 1 ? "s" : ""}</span>
            </p>
            <p className="text-xs text-slate-500">
              {STREAK_LABELS[fireLevel]}
            </p>
            {streakDays >= 3 && (
              <p className="text-[10px] text-amber-400 mt-0.5">2x XP bonus active!</p>
            )}
          </div>
        </div>
      </section>

      {/* Progress cards */}
      <section>
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Your Progress</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="card">
            <p className="text-sm font-medium text-slate-400">Lessons Completed</p>
            <p className="mt-2 text-3xl font-bold text-emerald-400">
              {isReady ? `${lessonsCompleted} / ${totalLessons || "..."}` : "..."}
            </p>
            <p className="mt-1 text-sm text-slate-500">
              {lessonsCompleted > 0 ? `${stats?.lessonsInProgress ?? 0} in progress` : "Open your first lesson"}
            </p>
          </div>
          <div className="card">
            <p className="text-sm font-medium text-slate-400">Exercises Passed</p>
            <p className="mt-2 text-3xl font-bold text-amber-400">
              {isReady ? String(stats?.exercisesPassed ?? 0) : "..."}
            </p>
            <p className="mt-1 text-sm text-slate-500">
              {(stats?.totalSubmissions ?? 0) > 0 ? `${stats?.totalSubmissions} submissions` : "Submit your first exercise"}
            </p>
          </div>
          <div className="card">
            <p className="text-sm font-medium text-slate-400">Quizzes Completed</p>
            <p className="mt-2 text-3xl font-bold text-primary-400">
              {isReady ? String(stats?.quizzesCompleted ?? 0) : "..."}
            </p>
            <p className="mt-1 text-sm text-slate-500">
              {(stats?.quizzesCompleted ?? 0) > 0 ? "Keep testing yourself" : "Take your first quiz"}
            </p>
          </div>
          <div className="card">
            <p className="text-sm font-medium text-slate-400">Achievements</p>
            <p className="mt-2 text-3xl font-bold text-purple-400">
              {unlockedCount} / {ACHIEVEMENTS.length}
            </p>
            <p className="mt-1 text-sm text-slate-500">
              {unlockedCount > 0 ? "Collect them all!" : "Start earning badges"}
            </p>
          </div>
        </div>
      </section>

      {/* Achievements */}
      <section>
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Achievements</h2>
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-6">
          {ACHIEVEMENTS.map((a) => {
            const unlocked = state.unlockedAchievements.includes(a.id);
            return (
              <div
                key={a.id}
                className={`rounded-xl border p-4 text-center transition-all ${
                  unlocked
                    ? "border-amber-500/30 bg-amber-500/5 shadow-lg shadow-amber-500/5"
                    : "border-slate-700/50 bg-surface-800 opacity-40"
                }`}
                title={a.description}
              >
                <div className="text-3xl mb-2">{a.icon}</div>
                <p className={`text-xs font-medium ${unlocked ? "text-amber-300" : "text-slate-500"}`}>
                  {a.title}
                </p>
                {!unlocked && (
                  <p className="text-[10px] text-slate-600 mt-1">🔒 Locked</p>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Quick links */}
      <section>
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Quick Start</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Link href="/learn/phases" className="card group transition-all hover:border-primary-500/50 hover:shadow-primary-500/10">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-600/20 text-primary-400">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-slate-100 group-hover:text-primary-300 transition-colors">Browse Curriculum</h3>
                <p className="text-sm text-slate-400">Explore all 12 phases and 35 lessons</p>
              </div>
            </div>
          </Link>
          <Link href="/learn/lessons/phase-01--lesson-01" className="card group transition-all hover:border-emerald-500/50 hover:shadow-emerald-500/10">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-600/20 text-emerald-400">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-slate-100 group-hover:text-emerald-300 transition-colors">Begin Phase 1</h3>
                <p className="text-sm text-slate-400">Terminal, Git & Python setup</p>
              </div>
            </div>
          </Link>
          <Link href="/projects" className="card group transition-all hover:border-amber-500/50 hover:shadow-amber-500/10">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-amber-600/20 text-amber-400">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-slate-100 group-hover:text-amber-300 transition-colors">Capstone Projects</h3>
                <p className="text-sm text-slate-400">15 real-world AI projects</p>
              </div>
            </div>
          </Link>
        </div>
      </section>
    </div>
  );
}
