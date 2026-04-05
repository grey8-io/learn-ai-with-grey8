"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchManifest, ManifestPhase } from "@/lib/api";
import { useProgress } from "@/components/ProgressProvider";
import type { LessonStatus } from "@/lib/progress";

function PhaseCard({
  phase,
  progressMap,
}: {
  phase: ManifestPhase;
  progressMap: Map<string, LessonStatus>;
}) {
  const hasLessons = phase.lessons.length > 0;
  const completedCount = phase.lessons.filter(
    (l) => progressMap.get(l.id)?.status === "completed"
  ).length;
  const progressPct =
    hasLessons && completedCount > 0
      ? Math.round((completedCount / phase.lessons.length) * 100)
      : 0;

  return (
    <Link
      href={hasLessons ? `/learn/phases/${phase.phase}` : "#"}
      className={`card group relative transition-all ${
        hasLessons
          ? "hover:border-primary-500/50 hover:shadow-lg hover:shadow-primary-500/5 cursor-pointer"
          : "opacity-60 cursor-not-allowed"
      }`}
    >
      {/* Phase number badge */}
      <div
        className={`absolute -top-3 -left-3 flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold ${
          hasLessons
            ? "bg-primary-600 text-white shadow-lg shadow-primary-600/30"
            : "bg-slate-700 text-slate-400"
        }`}
      >
        {phase.phase}
      </div>

      <div className="pt-2">
        <h3
          className={`text-lg font-semibold ${
            hasLessons
              ? "text-slate-100 group-hover:text-primary-300 transition-colors"
              : "text-slate-400"
          }`}
        >
          {phase.title}
        </h3>

        {hasLessons && completedCount > 0 && (
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>{completedCount} / {phase.lessons.length} complete</span>
              <span>{progressPct}%</span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-slate-700">
              <div
                className="h-1.5 rounded-full bg-gradient-to-r from-emerald-600 to-emerald-400 transition-all"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>
        )}

        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            {phase.lessons.length} lesson{phase.lessons.length !== 1 ? "s" : ""}
          </span>
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
              hasLessons
                ? "bg-primary-600/20 text-primary-300"
                : "bg-slate-700/50 text-slate-500"
            }`}
          >
            {hasLessons ? "Available" : "Coming Soon"}
          </span>
        </div>

        {hasLessons && (
          <div className="mt-3 pt-3 border-t border-slate-700/50">
            <ul className="space-y-1">
              {phase.lessons.slice(0, 3).map((lesson) => (
                <li key={lesson.id} className="text-xs text-slate-400 truncate">
                  {lesson.title}
                </li>
              ))}
              {phase.lessons.length > 3 && (
                <li className="text-xs text-slate-500">
                  +{phase.lessons.length - 3} more
                </li>
              )}
            </ul>
          </div>
        )}
      </div>
    </Link>
  );
}

export default function PhasesPage() {
  const [phases, setPhases] = useState<ManifestPhase[]>([]);
  const [loading, setLoading] = useState(true);
  const [progressMap, setProgressMap] = useState<Map<string, LessonStatus>>(
    new Map()
  );
  const { backend } = useProgress();

  useEffect(() => {
    async function load() {
      try {
        const [manifest, allProgress] = await Promise.all([
          fetchManifest(),
          backend.getAllLessonProgress(),
        ]);
        setPhases(manifest.phases);
        const map = new Map<string, LessonStatus>();
        for (const p of allProgress) map.set(p.lessonId, p);
        setProgressMap(map);
      } catch (err) {
        console.error("Failed to load manifest:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [backend]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  const totalLessons = phases.reduce((sum, p) => sum + p.lessons.length, 0);
  const phasesWithContent = phases.filter((p) => p.lessons.length > 0).length;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Learning Phases</h1>
        <p className="mt-2 text-slate-400">
          {phases.length} phases taking you from beginner to AI engineer. Each
          phase includes lessons, exercises, and hands-on projects.
        </p>
      </div>

      {/* Progress bar */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-300">
            Curriculum Coverage
          </span>
          <span className="text-sm text-slate-400">
            {phasesWithContent} / {phases.length} phases &middot; {totalLessons}{" "}
            lessons available
          </span>
        </div>
        <div className="h-2 w-full rounded-full bg-slate-700">
          <div
            className="h-2 rounded-full bg-gradient-to-r from-primary-600 to-primary-400 transition-all"
            style={{
              width: `${
                phases.length > 0
                  ? (phasesWithContent / phases.length) * 100
                  : 0
              }%`,
            }}
          />
        </div>
      </div>

      {/* Phases grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {phases.map((phase) => (
          <PhaseCard key={phase.phase} phase={phase} progressMap={progressMap} />
        ))}
      </div>
    </div>
  );
}
