"use client";

import { useState } from "react";

const REPO_URL = "https://github.com/grey8-io/learn-ai-with-grey8";
/** Public raw path so the badge is downloadable even off the local install. */
const RAW_BADGE_BASE =
  "https://raw.githubusercontent.com/grey8-io/learn-ai-with-grey8/main/platform/web/public/badges";

interface BadgeShareActionsProps {
  /** Local (same-origin) badge path, e.g. "/badges/course-complete.png". */
  badgeSrc: string;
  /** Filename suggested when the learner saves the image. */
  downloadName: string;
  /** Caption text to copy and paste into the LinkedIn post. */
  caption: string;
}

/**
 * Share controls for a completion badge.
 *
 * LinkedIn's share endpoint only renders the Open Graph card of the URL it's
 * given — it ignores any image we pass and (on a local install) can't reach a
 * badge sitting on localhost. So the only way to get the BADGE onto LinkedIn is
 * for the learner to download it and attach it to a post themselves. These
 * controls make that flow obvious: download the image, copy the caption, open
 * LinkedIn, attach + paste.
 */
export default function BadgeShareActions({
  badgeSrc,
  downloadName,
  caption,
}: BadgeShareActionsProps) {
  const [copied, setCopied] = useState(false);
  // Derive the GitHub raw URL from the badge filename for an off-box fallback.
  const rawUrl = `${RAW_BADGE_BASE}/${badgeSrc.split("/").pop()}`;

  const copyCaption = async () => {
    try {
      await navigator.clipboard.writeText(caption);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard blocked (e.g. insecure context) — selection fallback.
      window.prompt("Copy the caption below:", caption);
    }
  };

  return (
    <div className="mt-6 space-y-4 text-left">
      {/* Step buttons */}
      <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
        <a
          href={badgeSrc}
          download={downloadName}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white transition-all hover:bg-emerald-500"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          1. Download badge
        </a>

        <button
          onClick={copyCaption}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-700 px-5 py-2.5 text-sm font-semibold text-white transition-all hover:bg-slate-600"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" />
          </svg>
          {copied ? "Caption copied!" : "2. Copy caption"}
        </button>

        <a
          href="https://www.linkedin.com/feed/"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#0A66C2] px-5 py-2.5 text-sm font-semibold text-white transition-all hover:bg-[#004182]"
        >
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
          </svg>
          3. Open LinkedIn
        </a>
      </div>

      {/* Instructions */}
      <div className="rounded-xl border border-slate-700/50 bg-surface-900/50 p-4 text-xs leading-relaxed text-slate-400">
        <p className="font-medium text-slate-300">How to post your badge</p>
        <ol className="mt-2 list-decimal space-y-1 pl-4">
          <li>Download the badge image above (or grab it from{" "}
            <a href={rawUrl} target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:text-primary-300">GitHub</a>).
          </li>
          <li>Copy the caption, then open LinkedIn and click <span className="text-slate-300">Start a post</span>.</li>
          <li>Attach the downloaded image and paste the caption.</li>
          <li>Post it — your network sees the badge, not just a link.</li>
        </ol>
        <p className="mt-2 text-slate-500">
          Tip: LinkedIn&apos;s one-click share only shows a link preview of the
          repo, so attaching the image yourself is what puts the badge front and
          center.
        </p>
      </div>
    </div>
  );
}
