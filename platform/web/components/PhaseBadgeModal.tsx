"use client";

import { useEffect } from "react";
import Image from "next/image";
import BadgeShareActions from "./BadgeShareActions";

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

function getShareCaption(phaseNumber: number, phaseTitle: string): string {
  return `I just completed Phase ${phaseNumber} (${phaseTitle}) of Learn AI With Grey8 — a free, open-source AI bootcamp that runs 100% locally.\n\nIf you want to learn AI application development without expensive subscriptions or cloud API keys, check it out:\n${REPO_URL}\n\n#LearnAI #OpenSource #Grey8 #AIBootcamp #ArtificialIntelligence`;
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

  return (
    <div className="fixed inset-0 z-[90] flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 mx-4 max-h-[90vh] w-full max-w-md overflow-y-auto rounded-2xl border border-slate-700/50 bg-surface-800 p-8 text-center shadow-2xl">
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

        {/* Download badge + share instructions */}
        <BadgeShareActions
          badgeSrc={getBadgeSrc(phaseNumber)}
          downloadName={`grey8-phase-${String(phaseNumber).padStart(2, "0")}.png`}
          caption={getShareCaption(phaseNumber, phaseTitle)}
        />

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
