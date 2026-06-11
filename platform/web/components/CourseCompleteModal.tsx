"use client";

import { useEffect } from "react";
import Image from "next/image";
import {
  getCourseBadgeSrc,
  getCourseShareCaption,
} from "@/lib/course-completion";
import BadgeShareActions from "./BadgeShareActions";

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

  return (
    <div className="fixed inset-0 z-[95] flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 mx-4 max-h-[90vh] w-full max-w-md overflow-y-auto rounded-2xl border border-amber-500/40 bg-surface-800 p-8 text-center shadow-2xl">
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

        {/* Download badge + share instructions */}
        <BadgeShareActions
          badgeSrc={getCourseBadgeSrc()}
          downloadName="grey8-course-complete.png"
          caption={getCourseShareCaption()}
        />

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
