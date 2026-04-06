"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import MarkdownRenderer from "@/components/MarkdownRenderer";

const ChatPanel = dynamic(() => import("@/components/ChatPanel"), {
  ssr: false,
});
import { fetchLesson, fetchManifest, LessonData } from "@/lib/api";
import { useProgress } from "@/components/ProgressProvider";
import { useGamification } from "@/components/GamificationProvider";
import PhaseBadgeModal, {
  hasShownPhaseBadge,
  markPhaseBadgeShown,
} from "@/components/PhaseBadgeModal";
import type { LessonStatus } from "@/lib/progress";

/** Extract phase number from a lesson URL id like "phase-01--lesson-01" */
function getPhaseNumber(lessonId: string): number {
  const match = lessonId.match(/phase-(\d+)/);
  return match ? parseInt(match[1], 10) : 0;
}

const PASS_PERCENT = 70;

/** Calculate the minimum correct answers needed to pass a quiz at 70%. */
function quizPassCount(totalQuestions: number): number {
  return Math.ceil((PASS_PERCENT / 100) * totalQuestions);
}

export default function LessonPage({
  params,
}: {
  params: { lessonId: string };
}) {
  const [lesson, setLesson] = useState<LessonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<LessonStatus | null>(null);
  const [quizPassed, setQuizPassed] = useState(false);
  const [exercisePassed, setExercisePassed] = useState(false);
  const [quizScore, setQuizScore] = useState<number | null>(null);
  const [quizTotal, setQuizTotal] = useState<number>(5);
  const [exerciseScore, setExerciseScore] = useState<number | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [badgeModalOpen, setBadgeModalOpen] = useState(false);
  const [completedPhaseTitle, setCompletedPhaseTitle] = useState("");
  const { backend, refreshStats, stats } = useProgress();
  const { onLessonComplete, unlock, celebrate } = useGamification();

  // Decode lesson ID: URL uses -- separator, canonical uses /
  const canonicalId = params.lessonId.replace(/--/g, "/");
  const phaseNum = getPhaseNumber(params.lessonId);
  const isEasyPhase = phaseNum >= 1 && phaseNum <= 3;

  const loadProgress = useCallback(async () => {
    const p = await backend.getLessonProgress(canonicalId);
    setProgress(p);
  }, [backend, canonicalId]);

  /** Check quiz + exercise status and auto-complete if requirements are met */
  const checkCompletion = useCallback(async (lessonData: LessonData) => {
    // Fetch quiz and exercise results in parallel
    const hasExercise = lessonData.exercises.length > 0;
    const [quizResult, bestSub] = await Promise.all([
      backend.getQuizResult(params.lessonId),
      hasExercise ? backend.getBestSubmission(lessonData.exercises[0].id) : Promise.resolve(null),
    ]);

    const qTotal = quizResult?.answers?.length ?? 0;
    const qPassed = quizResult !== null && qTotal > 0 && quizResult.score >= quizPassCount(qTotal);
    setQuizPassed(qPassed);
    setQuizScore(quizResult?.score ?? null);
    if (qTotal > 0) setQuizTotal(qTotal);

    const exPassed = hasExercise
      ? bestSub !== null && (bestSub.score ?? 0) >= PASS_PERCENT
      : true;
    setExercisePassed(exPassed);
    setExerciseScore(bestSub?.score ?? null);

    // Auto-complete: easy phases need quiz only, others need both
    const shouldComplete = isEasyPhase ? qPassed : (qPassed && exPassed);
    if (shouldComplete) {
      // Only award XP if not already completed
      const prev = await backend.getLessonProgress(canonicalId);
      await backend.upsertLessonProgress(canonicalId, "completed");
      const p = await backend.getLessonProgress(canonicalId);
      setProgress(p);
      refreshStats();
      const wasNewCompletion = prev?.status !== "completed";
      if (wasNewCompletion) {
        onLessonComplete(stats?.currentStreakDays ?? 0);

        // Check if this completion finishes the entire phase
        if (!hasShownPhaseBadge(phaseNum)) {
          try {
            const manifest = await fetchManifest();
            const phase = manifest.phases.find((ph) => ph.phase === phaseNum);
            if (phase) {
              const allProgress = await backend.getAllLessonProgress();
              const completedSet = new Set(
                allProgress.filter((lp) => lp.status === "completed").map((lp) => lp.lessonId)
              );
              const allDone = phase.lessons.every((l) => completedSet.has(l.id));
              if (allDone) {
                markPhaseBadgeShown(phaseNum);
                setCompletedPhaseTitle(phase.title);
                unlock("phase_crusher");
                if (manifest.phases.filter((ph) =>
                  ph.lessons.every((l) => completedSet.has(l.id))
                ).length >= 5) {
                  unlock("five_phases");
                }
                if (manifest.phases.every((ph) =>
                  ph.lessons.every((l) => completedSet.has(l.id))
                )) {
                  unlock("full_stack");
                }
                celebrate();
                setBadgeModalOpen(true);
              }
            }
          } catch {
            // Manifest fetch failed — skip badge check silently
          }
        }
      }
    }
  }, [backend, params.lessonId, canonicalId, isEasyPhase, phaseNum, refreshStats, onLessonComplete, stats, unlock, celebrate]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchLesson(params.lessonId);
        setLesson(data);
        // Run progress upsert and completion check in parallel
        await Promise.all([
          backend.upsertLessonProgress(canonicalId, "in_progress").then(() => loadProgress()),
          checkCompletion(data),
        ]);
        refreshStats();
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load lesson"
        );
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [params.lessonId, backend, canonicalId, loadProgress, checkCompletion, refreshStats]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <h1 className="text-2xl font-bold text-slate-100">Lesson Not Found</h1>
        <p className="mt-2 text-sm text-slate-400">{error}</p>
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
        <Link
          href={`/learn/phases/${lesson.phaseId}`}
          className="hover:text-primary-400 transition-colors"
        >
          Phase {lesson.phaseId}
        </Link>
        <span>/</span>
        <span className="text-slate-200">{lesson.title}</span>
      </nav>

      {/* Objectives & metadata */}
      {lesson.objectives && lesson.objectives.length > 0 && (
        <div className="card max-w-4xl">
          <h2 className="text-lg font-semibold text-slate-100 mb-3">
            Learning Objectives
          </h2>
          <ul className="list-disc list-inside space-y-1 text-slate-300 text-sm">
            {lesson.objectives.map((obj, i) => (
              <li key={i}>{obj}</li>
            ))}
          </ul>
          {lesson.estimated_minutes > 0 && (
            <p className="mt-3 text-xs text-slate-500">
              Estimated time: {lesson.estimated_minutes} minutes
            </p>
          )}
        </div>
      )}

      {/* Lesson content */}
      <article className="card max-w-4xl">
        <MarkdownRenderer content={lesson.content} />
      </article>

      {/* Exercises */}
      {lesson.exercises.length > 0 && (
        <section className="max-w-4xl">
          <h2 className="text-xl font-semibold text-slate-100 mb-3">
            Exercises
          </h2>
          <div className="space-y-2">
            {lesson.exercises.map((ex) => (
              <Link
                key={ex.id}
                href={`/learn/exercises/${ex.id}`}
                className="flex items-center justify-between rounded-xl border border-slate-700/50 bg-surface-800 p-4 transition-all hover:border-primary-500/50"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-600/20 text-amber-400">
                    <svg
                      className="h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={2}
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5"
                      />
                    </svg>
                  </div>
                  <div>
                    <span className="font-medium text-slate-200">
                      {ex.title}
                    </span>
                    {ex.difficulty && (
                      <span
                        className={`ml-2 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          ex.difficulty === "easy"
                            ? "bg-emerald-600/20 text-emerald-300"
                            : ex.difficulty === "medium"
                            ? "bg-amber-600/20 text-amber-300"
                            : "bg-red-600/20 text-red-300"
                        }`}
                      >
                        {ex.difficulty}
                      </span>
                    )}
                  </div>
                </div>
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
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Quiz */}
      {lesson.hasQuiz && (
        <section className="max-w-4xl">
          <Link
            href={`/learn/quiz/${params.lessonId}`}
            className="flex items-center justify-between rounded-xl border border-primary-500/30 bg-primary-600/10 p-5 transition-all hover:border-primary-500/60 hover:bg-primary-600/20"
          >
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-600/20 text-primary-400">
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z"
                  />
                </svg>
              </div>
              <div>
                <span className="font-semibold text-slate-100">
                  Take the Quiz
                </span>
                <p className="text-sm text-slate-400">
                  Test your understanding of this lesson
                </p>
              </div>
            </div>
            <svg
              className="h-5 w-5 text-primary-400"
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
          </Link>
        </section>
      )}

      {/* Completion tracker */}
      <div className="max-w-4xl">
        {progress?.status === "completed" ? (
          <div className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
            <svg className="h-5 w-5 text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
            <span className="text-sm font-medium text-emerald-300">
              Lesson completed — nice work!
            </span>
          </div>
        ) : (
          <div className="card space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">
              To complete this lesson
            </h3>
            <div className="space-y-2">
              {/* Quiz requirement — always required */}
              <div className="flex items-center gap-3">
                <div className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full ${
                  quizPassed ? "bg-emerald-600 text-white" : "border border-slate-600 text-transparent"
                }`}>
                  {quizPassed && (
                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                    </svg>
                  )}
                </div>
                <span className={`text-sm ${quizPassed ? "text-emerald-300" : "text-slate-400"}`}>
                  Pass the quiz ({PASS_PERCENT}%+)
                  {quizScore !== null && !quizPassed && (
                    <span className="text-slate-500 ml-1">— current: {Math.round((quizScore / quizTotal) * 100)}%</span>
                  )}
                </span>
              </div>
              {/* Exercise requirement — phases 4-12 */}
              {lesson.exercises.length > 0 && (
                <div className="flex items-center gap-3">
                  <div className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full ${
                    exercisePassed
                      ? "bg-emerald-600 text-white"
                      : isEasyPhase
                      ? "bg-slate-700 text-slate-500"
                      : "border border-slate-600 text-transparent"
                  }`}>
                    {exercisePassed && (
                      <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                      </svg>
                    )}
                    {isEasyPhase && !exercisePassed && (
                      <span className="text-[8px]">—</span>
                    )}
                  </div>
                  <span className={`text-sm ${
                    exercisePassed
                      ? "text-emerald-300"
                      : isEasyPhase
                      ? "text-slate-500 line-through"
                      : "text-slate-400"
                  }`}>
                    Pass the exercise ({PASS_PERCENT}%+)
                    {isEasyPhase && <span className="no-underline ml-1 text-slate-600">— not required for this phase</span>}
                    {!isEasyPhase && exerciseScore !== null && !exercisePassed && (
                      <span className="text-slate-500 ml-1">— best: {exerciseScore}%</span>
                    )}
                  </span>
                </div>
              )}
            </div>

            {/* "I already know this" shortcut */}
            {!quizPassed && (
              <div className="pt-3 border-t border-slate-700/50">
                <div className="flex items-start gap-3">
                  <svg className="h-5 w-5 shrink-0 text-primary-400 mt-0.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75Z" />
                  </svg>
                  <div>
                    <p className="text-sm text-slate-300">
                      <strong className="text-slate-200">Already know this?</strong>{" "}
                      {isEasyPhase
                        ? "Pass the quiz to skip ahead."
                        : "Pass the quiz and the exercise to skip ahead."
                      }
                    </p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <Link
                        href={`/learn/quiz/${params.lessonId}`}
                        className="inline-flex items-center rounded-lg bg-primary-600/15 px-3 py-1.5 text-xs font-medium text-primary-300 hover:bg-primary-600/25 transition-colors"
                      >
                        Go to Quiz
                        <svg className="ml-1.5 h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                        </svg>
                      </Link>
                      {!isEasyPhase && lesson.exercises.length > 0 && !exercisePassed && (
                        <Link
                          href={`/learn/exercises/${lesson.exercises[0].id}`}
                          className="inline-flex items-center rounded-lg bg-amber-600/15 px-3 py-1.5 text-xs font-medium text-amber-300 hover:bg-amber-600/25 transition-colors"
                        >
                          Go to Exercise
                          <svg className="ml-1.5 h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                          </svg>
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex items-center justify-between max-w-4xl pt-4 border-t border-slate-700/50">
        {lesson.prevLesson ? (
          <Link
            href={`/learn/lessons/${lesson.prevLesson}`}
            className="btn-secondary"
          >
            <svg
              className="mr-2 h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15.75 19.5 8.25 12l7.5-7.5"
              />
            </svg>
            Previous Lesson
          </Link>
        ) : (
          <div />
        )}
        {lesson.nextLesson ? (
          <Link
            href={`/learn/lessons/${lesson.nextLesson}`}
            className="btn-primary"
          >
            Next Lesson
            <svg
              className="ml-2 h-4 w-4"
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
          </Link>
        ) : (
          <div />
        )}
      </nav>

      {/* Floating tutor button */}
      <button
        onClick={() => setChatOpen(true)}
        className="fixed bottom-6 right-6 z-[60] flex h-14 w-14 items-center justify-center rounded-full bg-primary-600 text-white shadow-lg shadow-primary-600/30 hover:bg-primary-500 transition-all hover:scale-105 print:hidden"
        title="Ask AI Tutor"
      >
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z" />
        </svg>
      </button>

      {/* Chat panel */}
      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        lessonId={params.lessonId}
      />

      {/* Phase completion badge modal */}
      <PhaseBadgeModal
        open={badgeModalOpen}
        onClose={() => setBadgeModalOpen(false)}
        phaseNumber={phaseNum}
        phaseTitle={completedPhaseTitle}
      />
    </div>
  );
}
