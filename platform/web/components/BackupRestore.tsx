"use client";

import { useRef, useState } from "react";
import { downloadBackup, importBackup } from "@/lib/backup";

/**
 * Backup & restore card for anonymous (local-only) learners.
 *
 * Export downloads all progress + gamification state as a JSON file; import
 * reads it back and reloads so every provider re-reads localStorage. This is
 * the lifeboat for learners who clear site data or switch browser/machine
 * without signing in.
 */
export default function BackupRestore() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<
    { kind: "success" | "error"; message: string } | null
  >(null);

  function handleExport() {
    try {
      downloadBackup();
      setStatus({
        kind: "success",
        message: "Progress downloaded. Keep the file somewhere safe.",
      });
    } catch {
      setStatus({ kind: "error", message: "Couldn't create the backup file." });
    }
  }

  function handleImportClick() {
    setStatus(null);
    fileInputRef.current?.click();
  }

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    // Reset so picking the same file again re-triggers onChange.
    e.target.value = "";
    if (!file) return;

    const ok = window.confirm(
      "Importing will overwrite your current progress on this browser with the contents of the backup. Continue?"
    );
    if (!ok) return;

    try {
      const text = await file.text();
      const { keysRestored } = importBackup(text);
      setStatus({
        kind: "success",
        message: `Restored ${keysRestored} item${keysRestored === 1 ? "" : "s"}. Reloading…`,
      });
      // Reload so ProgressProvider + GamificationProvider re-read localStorage.
      setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      setStatus({
        kind: "error",
        message: err instanceof Error ? err.message : "Import failed.",
      });
    }
  }

  return (
    <div className="card">
      <div className="flex items-start gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-slate-700/40 text-slate-300">
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-100">Backup &amp; Restore Progress</h3>
          <p className="mt-1 text-sm text-slate-400">
            Save all your progress, XP, and achievements to a file. Import it
            later if you clear your browser data or move to another browser or
            computer.
          </p>

          <div className="mt-4 flex flex-wrap gap-3">
            <button type="button" onClick={handleExport} className="btn-secondary text-sm">
              Download backup
            </button>
            <button type="button" onClick={handleImportClick} className="btn-secondary text-sm">
              Import backup
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/json,.json"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          {status && (
            <p
              className={`mt-3 text-sm ${
                status.kind === "success" ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {status.message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
