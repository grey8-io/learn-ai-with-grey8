"use client";

import { useEffect } from "react";
import Image from "next/image";
import {
  getCourseBadgeSrc,
  getCourseLinkedInShareUrl,
} from "@/lib/course-completion";

interface CourseCompleteModalProps {
  open: boolean;
  onClose: () => void;
}

/**
 * Grand-finale modal shown once a learner has completed every lesson in all 12
 * phases. Mirrors PhaseBadgeModal's styling but uses the course-complete badge
 * and a whole-bootcamp LinkedIn share — the most valuable share in the funnel.
 */
export default function CourseCompleteModal({
  open,
  onClose,
}: CourseCompleteModalProps) {
  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;

  const shareUrl = getCourseLinkedInShareUrl();

  return (
    <div className="fixed inset-0 z-[95] flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 mx-4 w-full max-w-md rounded-2xl border border-amber-500/40 bg-surface-800 p-8 text-center shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute right-4 top-4 text-slate-500 hover:text-slate-300 transition-colors"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Badge image */}
        <div className="mx-auto mb-6 h-48 w-48 relative">
          <Image
            src={getCourseBadgeSrc()}
            alt="Course completion badge"
            fill
            className="object-contain"
            priority
          />
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-slate-100">
          🎓 Course Complete!
        </h2>
        <p className="mt-2 text-slate-400">
          You finished the entire{" "}
          <span className="text-slate-200 font-medium">Learn AI With Grey8</span>{" "}
          bootcamp — all 39 lessons across 12 phases.
        </p>

        {/* Share on LinkedIn */}
        <a
          href={shareUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[#0A66C2] px-6 py-3 text-sm font-semibold text-white transition-all hover:bg-[#004182] hover:scale-105"
        >
          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
          </svg>
          Share on LinkedIn
        </a>

        {/* Secondary actions */}
        <div className="mt-4 flex items-center justify-center gap-4">
          <button
            onClick={onClose}
            className="text-sm text-slate-500 hover:text-slate-300 transition-colors"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
