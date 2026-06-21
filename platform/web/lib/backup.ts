/**
 * Local progress backup & restore.
 *
 * Anonymous learners keep all their progress in localStorage. If they clear
 * site data, switch browsers, or move to a new machine, that progress is lost.
 * This module lets them export everything to a single JSON file and import it
 * back later — a portable save file that needs no account or Supabase.
 *
 * It captures every key under the app's localStorage namespaces, so it covers
 * lesson progress, exercise submissions, quiz results, tutor chats AND the
 * gamification state (XP, level, achievements, streak) plus badge flags.
 * New keys added under these prefixes are picked up automatically.
 */

/** localStorage key prefixes owned by the app. Anything outside these is never
 *  exported or restored — so an imported file can't write arbitrary keys. */
const NAMESPACES = ["progress:", "gamification:", "badges:"] as const;

const APP_ID = "learn-ai-with-grey8";
const BACKUP_TYPE = "progress-backup";
const BACKUP_VERSION = 1;

export interface BackupFile {
  app: string;
  type: string;
  version: number;
  exportedAt: string;
  /** key -> parsed JSON value (stored decoded for human readability) */
  data: Record<string, unknown>;
}

function isClient(): boolean {
  return typeof window !== "undefined";
}

function isOwnedKey(key: string): boolean {
  return NAMESPACES.some((ns) => key.startsWith(ns));
}

/** Snapshot all app-owned localStorage keys into a backup object. */
export function exportBackup(): BackupFile {
  const data: Record<string, unknown> = {};
  if (isClient()) {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key || !isOwnedKey(key)) continue;
      const raw = localStorage.getItem(key);
      if (raw === null) continue;
      try {
        data[key] = JSON.parse(raw);
      } catch {
        // Non-JSON value (e.g. a plain flag) — keep it verbatim.
        data[key] = raw;
      }
    }
  }
  return {
    app: APP_ID,
    type: BACKUP_TYPE,
    version: BACKUP_VERSION,
    exportedAt: new Date().toISOString(),
    data,
  };
}

/** Trigger a browser download of the current progress as a JSON file. */
export function downloadBackup(): void {
  if (!isClient()) return;
  const backup = exportBackup();
  const blob = new Blob([JSON.stringify(backup, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const stamp = backup.exportedAt.slice(0, 10); // YYYY-MM-DD
  const a = document.createElement("a");
  a.href = url;
  a.download = `grey8-progress-${stamp}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export interface ImportResult {
  keysRestored: number;
}

/**
 * Restore progress from a backup file's text.
 * Validates the file shape, then writes back only app-owned keys.
 * Throws an Error with a human-readable message on invalid input.
 */
export function importBackup(jsonText: string): ImportResult {
  if (!isClient()) {
    throw new Error("Import is only available in the browser.");
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(jsonText);
  } catch {
    throw new Error("That file isn't valid JSON. Pick the .json file you downloaded.");
  }

  if (typeof parsed !== "object" || parsed === null) {
    throw new Error("Unrecognized backup file.");
  }

  const backup = parsed as Partial<BackupFile>;
  if (backup.app !== APP_ID || backup.type !== BACKUP_TYPE) {
    throw new Error("This doesn't look like a Learn AI With Grey8 progress backup.");
  }
  if (typeof backup.data !== "object" || backup.data === null) {
    throw new Error("Backup file is missing its progress data.");
  }

  let keysRestored = 0;
  for (const [key, value] of Object.entries(backup.data)) {
    if (!isOwnedKey(key)) continue; // ignore anything outside our namespaces
    try {
      const raw = typeof value === "string" ? value : JSON.stringify(value);
      localStorage.setItem(key, raw);
      keysRestored++;
    } catch {
      // Skip keys that fail to write (e.g. storage full) rather than aborting.
    }
  }

  if (keysRestored === 0) {
    throw new Error("No progress data found in that file.");
  }

  return { keysRestored };
}
