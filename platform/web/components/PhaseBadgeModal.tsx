"use client";

import { useEffect } from "react";
import Image from "next/image";

interface PhaseBadgeModalProps {
  open: boolean;
  onClose: () => void;
  phaseNumber: number;
  phaseTitle: string;
}

const REPO_URL = "https://github.com/grey8-io/learn-ai-with-grey8";

function getBadgeSrc(phaseNumber: number): string {
  return `/badges/phase-${String(phaseNumber).padStart(2, "0")}.png`;
}

function getLinkedInShareUrl(phaseNumber: number, phaseTitle: string): string {
  const text = `I just completed Phase ${phaseNumber} (${phaseTitle}) of Learn AI With Grey8 — a free, open-source AI bootcamp that runs 100% locally.\n\nIf you want to learn AI application development without expensive subscriptions or cloud API keys, check it out:\n${REPO_URL}\n\n#LearnAI #OpenSource #Grey8 #AIBootcamp #ArtificialIntelligence`;
  return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(REPO_URL)}&summary=${encodeURIComponent(text)}`;
}

/** Tracks which phase badges have already been shown so we don't repeat. */
const SHOWN_KEY = "badges:phases_shown";

export function hasShownPhaseBadge(phaseNumber: number): boolean {
  if (typeof window === "undefined") return true;
  try {
    const shown = JSON.parse(localStorage.getItem(SHOWN_KEY) || "[]") as number[];
    return shown.includes(phaseNumber);
  } catch {
    return false;
  }
}

export function markPhaseBadgeShown(phaseNumber: number): void {
  if (typeof window === "undefined") return;
  try {
    const shown = JSON.parse(localStorage.getItem(SHOWN_KEY) || "[]") as number[];
    if (!shown.includes(phaseNumber)) {
      shown.push(phaseNumber);
      localStorage.setItem(SHOWN_KEY, JSON.stringify(shown));
    }
  } catch {
    // ignore
  }
}

export default function PhaseBadgeModal({
  open,
  onClose,
  phaseNumber,
  phaseTitle,
}: PhaseBadgeModalProps) {
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

  const shareUrl = getLinkedInShareUrl(phaseNumber, phaseTitle);

  return (
    <div className="fixed inset-0 z-[90] flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 mx-4 w-full max-w-md rounded-2xl border border-slate-700/50 bg-surface-800 p-8 text-center shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-500 hover:text-slate-300 transition-colors"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Badge image */}
        <div className="mx-auto mb-6 h-48 w-48 relative">
          <Image
            src={getBadgeSrc(phaseNumber)}
            alt={`Phase ${phaseNumber} completion badge`}
            fill
            className="object-contain"
          />
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-slate-100">
          Phase {phaseNumber} Complete!
        </h2>
        <p className="mt-2 text-slate-400">
          You crushed <span className="text-slate-200 font-medium">{phaseTitle}</span>
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
            Continue learning
          </button>
        </div>
      </div>
    </div>
  );
}
