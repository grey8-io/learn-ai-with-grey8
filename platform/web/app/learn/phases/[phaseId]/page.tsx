"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchManifest, ManifestPhase } from "@/lib/api";
import { useProgress } from "@/components/ProgressProvider";
import type { LessonStatus } from "@/lib/progress";

function StatusIcon({ status }: { status?: string }) {
  if (status === "completed") {
    return (
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-600/20 text-emerald-400">
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
        </svg>
      </div>
    );
  }
  if (status === "in_progress") {
    return (
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-600/20 text-primary-400">
        <div className="h-3 w-3 rounded-full bg-primary-400" />
      </div>
    );
  }
  return (
    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-700/50 text-slate-500">
      <div className="h-3 w-3 rounded-full bg-slate-600" />
    </div>
  );
}

export default function PhasePage({
  params,
}: {
  params: { phaseId: string };
}) {
  const [phase, setPhase] = useState<ManifestPhase | null>(null);
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
        const found = manifest.phases.find(
          (p) => String(p.phase) === params.phaseId
        );
        setPhase(found || null);
        const map = new Map<string, LessonStatus>();
        for (const p of allProgress) map.set(p.lessonId, p);
        setProgressMap(map);
      } catch (err) {
        console.error("Failed to load phase:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [params.phaseId, backend]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (!phase) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <h1 className="text-2xl font-bold text-slate-100">Phase Not Found</h1>
        <p className="mt-2 text-slate-400">
          This phase is not yet available or does not exist.
        </p>
        <Link href="/learn/phases" className="btn-primary mt-6">
          Back to Phases
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-slate-400">
        <Link
          href="/learn/phases"
          className="hover:text-primary-400 transition-colors"
        >
          Phases
        </Link>
        <span>/</span>
        <span className="text-slate-200">Phase {phase.phase}</span>
      </nav>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-100">
          Phase {phase.phase}: {phase.title}
        </h1>
        {phase.lessons.length === 0 && (
          <p className="mt-3 text-lg text-slate-400">
            Content for this phase is coming soon.
          </p>
        )}
      </div>

      {/* Progress */}
      {phase.lessons.length > 0 && (() => {
        const completed = phase.lessons.filter(
          (l) => progressMap.get(l.id)?.status === "completed"
        ).length;
        const pct = Math.round((completed / phase.lessons.length) * 100);
        return (
          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-slate-300">
                Phase Progress
              </span>
              <span className="text-sm text-slate-400">
                {completed} / {phase.lessons.length} lessons
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-slate-700">
              <div
                className="h-2 rounded-full bg-gradient-to-r from-primary-600 to-primary-400 transition-all"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })()}

      {/* Lessons list */}
      {phase.lessons.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-xl font-semibold text-slate-100">Lessons</h2>
          <div className="space-y-2">
            {phase.lessons.map((lesson, index) => {
              const encodedId = lesson.id.replace(/\//g, "--");
              return (
                <Link
                  key={lesson.id}
                  href={`/learn/lessons/${encodedId}`}
                  className="flex items-center gap-4 rounded-xl border border-slate-700/50 bg-surface-800 p-4 transition-all hover:border-primary-500/50 hover:bg-surface-800/80"
                >
                  <StatusIcon status={progressMap.get(lesson.id)?.status} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-slate-500">
                        {index + 1}.
                      </span>
                      <h3 className="font-medium text-slate-100">
                        {lesson.title}
                      </h3>
                    </div>
                    {lesson.objectives.length > 0 && (
                      <p className="mt-1 text-xs text-slate-500 truncate">
                        {lesson.objectives[0]}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-xs text-slate-500">
                      {lesson.estimated_minutes} min
                    </span>
                    <span className="text-xs text-slate-600">
                      {lesson.exercises.length} exercise
                      {lesson.exercises.length !== 1 ? "s" : ""}
                    </span>
                    <svg
                      className="h-4 w-4 text-slate-500"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={2}
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="m8.25 4.5 7.5 7.5-7.5 7.5"
                      />
                    </svg>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
