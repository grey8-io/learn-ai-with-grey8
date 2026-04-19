"use client";

import Link from "next/link";

export default function AuthDisabledNotice() {
  return (
    <div className="card text-center">
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-700/40 text-slate-300">
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
        </svg>
      </div>
      <h1 className="text-xl font-bold text-slate-100">Sign-in is not enabled</h1>
      <p className="mt-2 text-sm text-slate-400">
        This deployment runs without an authentication backend. Your progress is
        being saved locally in this browser and will persist across refreshes
        and restarts.
      </p>
      <p className="mt-2 text-sm text-slate-400">
        Sign-in is an optional feature for multi-device sync and team
        deployments. See the project docs to enable it.
      </p>
      <Link href="/" className="btn-primary mt-6 inline-block">
        Back to dashboard
      </Link>
    </div>
  );
}
