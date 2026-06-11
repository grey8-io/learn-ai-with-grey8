"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { useProgress } from "@/components/ProgressProvider";
import { fetchManifest } from "@/lib/api";
import CourseCompleteModal from "@/components/CourseCompleteModal";
import {
  isCourseComplete,
  getCourseBadgeSrc,
  getCourseLinkedInShareUrl,
} from "@/lib/course-completion";

/**
 * Persistent dashboard banner that appears once a learner has completed every
 * lesson in all 12 phases. Unlike the one-time finale modal, this stays
 * available so they can share their completion on LinkedIn whenever they like
 * (people often post a credential days later) — the highest-value share in the
 * funnel, always one click away.
 */
export default function CourseCompleteCard() {
  const { backend, isReady } = useProgress();
  const [complete, setComplete] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    if (!isReady) return;
    let cancelled = false;
    (async () => {
      try {
        const [manifest, allProgress] = await Promise.all([
          fetchManifest(),
          backend.getAllLessonProgress(),
        ]);
        const completedIds = allProgress
          .filter((lp) => lp.status === "completed")
          .map((lp) => lp.lessonId);
        if (!cancelled) {
          setComplete(isCourseComplete(manifest, completedIds));
        }
      } catch {
        // Best-effort — never block the dashboard on this check.
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [backend, isReady]);

  if (!complete) return null;

  const shareUrl = getCourseLinkedInShareUrl();

  return (
    <section className="flex flex-col items-center gap-5 rounded-2xl border border-amber-500/40 bg-gradient-to-br from-amber-500/10 via-surface-800 to-surface-800 p-6 sm:flex-row sm:gap-6 sm:p-8">
      <button
        onClick={() => setModalOpen(true)}
        aria-label="View course completion badge"
        className="relative h-24 w-24 shrink-0 transition-transform hover:scale-105"
      >
        <Image
          src={getCourseBadgeSrc()}
          alt="Course completion badge"
          fill
          className="object-contain"
        />
      </button>

      <div className="flex-1 text-center sm:text-left">
        <h2 className="text-xl font-bold text-slate-100">
          🎓 You completed the entire bootcamp!
        </h2>
        <p className="mt-1 text-sm text-slate-400">
          All 39 lessons across 12 phases. Share your achievement — it&apos;s a
          credential worth showing off.
        </p>
      </div>

      <div className="flex shrink-0 flex-col gap-2">
        <a
          href={shareUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#0A66C2] px-5 py-2.5 text-sm font-semibold text-white transition-all hover:bg-[#004182] hover:scale-105"
        >
          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
          </svg>
          Share on LinkedIn
        </a>
        <button
          onClick={() => setModalOpen(true)}
          className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
        >
          View badge
        </button>
      </div>

      <CourseCompleteModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </section>
  );
}
