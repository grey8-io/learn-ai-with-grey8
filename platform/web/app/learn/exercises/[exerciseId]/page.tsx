"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import CodeEditor from "@/components/CodeEditor";
import ExerciseResult from "@/components/ExerciseResult";
import ChatPanel from "@/components/ChatPanel";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import { fetchExercise, submitCode, getHint, fetchSolution, ExerciseData } from "@/lib/api";
import { useProgress } from "@/components/ProgressProvider";
import { useGamification } from "@/components/GamificationProvider";
import type { Submission } from "@/lib/progress";

interface GradeResult {
  score: number;
  passed: boolean;
  tests: { name: string; passed: boolean; message?: string }[];
  feedback: string;
}

export default function ExercisePage({
  params,
}: {
  params: { exerciseId: string };
}) {
  const [exercise, setExercise] = useState<ExerciseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [code, setCode] = useState("");
  const [result, setResult] = useState<GradeResult | null>(null);
  const [hint, setHint] = useState<string | null>(null);
  const [hintLevel, setHintLevel] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [loadingHint, setLoadingHint] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [bestScore, setBestScore] = useState<number | null>(null);
  const [attemptCount, setAttemptCount] = useState(0);
  const [showSolution, setShowSolution] = useState(false);
  const [solutionCode, setSolutionCode] = useState<string | null>(null);
  const { backend, refreshStats, stats } = useProgress();
  const { onExerciseComplete, onHintUsed } = useGamification();

  const SOLUTION_REVEAL_THRESHOLD = 5;

  // Track which exerciseId we've already initialized the editor for, so that
  // backend changes or effect re-runs NEVER overwrite a student's in-progress
  // typing with the starter or their last submission.
  const initializedForRef = useRef<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const isInitialLoad = initializedForRef.current !== params.exerciseId;

    async function load() {
      // Primary fetch — only this failing should show "not found".
      let data: ExerciseData;
      try {
        data = await fetchExercise(params.exerciseId);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load exercise"
          );
          setLoading(false);
        }
        return;
      }
      if (cancelled) return;
      setExercise(data);
      if (isInitialLoad) {
        setCode(data.starterCode);
      }

      // Side-effects — failures here must not surface as a load error.
      try {
        const submissions = await backend.getSubmissions(params.exerciseId);
        if (cancelled) return;
        setAttemptCount(submissions.length);
        const best = await backend.getBestSubmission(params.exerciseId);
        if (cancelled) return;
        if (best) {
          setBestScore(best.score);
          if (isInitialLoad) {
            setCode(best.code);
          }
        }
      } catch (sideEffectErr) {
        console.warn("Exercise side effects failed:", sideEffectErr);
      }

      if (!cancelled) {
        initializedForRef.current = params.exerciseId;
        setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [params.exerciseId, backend]);

  async function handleSubmit() {
    setSubmitting(true);
    setResult(null);
    try {
      const data = await submitCode(params.exerciseId, code);
      setResult(data);
      // Persist submission
      await backend.addSubmission({
        exerciseId: params.exerciseId,
        code,
        score: data.score,
        testPassed: data.passed,
        testResults: data.tests,
        rubricScore: null,
        rubricFeedback: data.feedback,
        submittedAt: new Date().toISOString(),
      });
      setBestScore((prev) =>
        Math.max(prev ?? 0, data.score)
      );
      setAttemptCount((prev) => prev + 1);

      // Auto-complete lesson if this submission passes (70%+)
      if (data.score >= 70 && exercise) {
        const quizId = exercise.lessonId; // quiz uses lesson URL id
        const canonicalLessonId = exercise.lessonId.replace(/--/g, "/");
        const quizResult = await backend.getQuizResult(quizId);
        // Need quiz passed too (70%+ correct)
        const quizTotal = quizResult?.answers?.length ?? 0;
        if (quizResult && quizTotal > 0 && quizResult.score >= Math.ceil(0.7 * quizTotal)) {
          await backend.upsertLessonProgress(canonicalLessonId, "completed");
        }
      }

      refreshStats();

      // Award XP for passing submissions
      if (data.score >= 70) {
        onExerciseComplete(data.score, stats?.currentStreakDays ?? 0);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setResult({
        score: 0,
        passed: false,
        tests: [],
        feedback: `Grading error: ${message}. Make sure the tutor service is running on port 8000.`,
      });
    } finally {
      setSubmitting(false);
    }
  }

  async function handleHint() {
    if (!exercise) return;
    setLoadingHint(true);
    const nextLevel = hintLevel + 1;

    // Use local hints from manifest first, then fall back to AI
    if (nextLevel <= exercise.hints.length) {
      setHint(exercise.hints[nextLevel - 1]);
      setHintLevel(nextLevel);
      onHintUsed(params.exerciseId);
      setLoadingHint(false);
      return;
    }

    // Beyond local hints, request from AI
    try {
      const data = await getHint(params.exerciseId, code, nextLevel);
      setHint(data.hint);
      setHintLevel(nextLevel);
    } catch {
      setHint("Unable to load hint. Please try again.");
    } finally {
      setLoadingHint(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !exercise) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <h1 className="text-2xl font-bold text-slate-100">
          Exercise Not Found
        </h1>
        <p className="mt-2 text-sm text-slate-400">{error}</p>
        <Link href="/learn/phases" className="btn-primary mt-6">
          Back to Phases
        </Link>
      </div>
    );
  }

  const maxHints = Math.max(exercise.hints.length, 3);

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col gap-4 -my-8 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-4">
      {/* Header bar */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <nav className="flex items-center gap-2 text-xs text-slate-500 mb-1">
            <Link
              href={`/learn/lessons/${exercise.lessonId}`}
              className="hover:text-primary-400 transition-colors"
            >
              {exercise.lessonTitle}
            </Link>
            <span>/</span>
            <span className="text-slate-400">{exercise.title}</span>
          </nav>
          <h1 className="text-xl font-bold text-slate-100">
            {exercise.title}
          </h1>
          <p className="text-sm text-slate-400">
            Phase {exercise.phaseId}
            {bestScore !== null && (
              <span className={`ml-2 ${bestScore >= 70 ? "text-emerald-400" : "text-amber-400"}`}>
                Best: {bestScore}%
              </span>
            )}
            {" "}&middot;{" "}
            <span
              className={`${
                exercise.difficulty === "easy"
                  ? "text-emerald-400"
                  : exercise.difficulty === "medium"
                  ? "text-amber-400"
                  : "text-red-400"
              }`}
            >
              {exercise.difficulty}
            </span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleHint}
            disabled={loadingHint || submitting || hintLevel >= maxHints}
            className="btn-secondary text-sm"
          >
            {loadingHint ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-transparent mr-2" />
            ) : (
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
                  d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18"
                />
              </svg>
            )}
            Hint {hintLevel > 0 ? `(${hintLevel}/${maxHints})` : ""}
          </button>
          <button
            onClick={() => setChatOpen(!chatOpen)}
            className="btn-secondary text-sm"
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
                d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 0 1-.825-.242m9.345-8.334a2.126 2.126 0 0 0-.476-.095 48.64 48.64 0 0 0-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0 0 11.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155"
              />
            </svg>
            Tutor
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="btn-primary text-sm"
          >
            {submitting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2" />
                Grading...
              </>
            ) : (
              <>
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
                    d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z"
                  />
                </svg>
                Submit
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main split layout */}
      <div className="flex flex-1 gap-4 min-h-0">
        {/* Left: Instructions (rubric rendered as markdown) */}
        <div className="w-1/2 overflow-auto rounded-xl border border-slate-700/50 bg-surface-800 p-6">
          {/* Hint display — shown at top so it's immediately visible */}
          {hint && (
            <div className="mb-6 rounded-lg border border-amber-600/30 bg-amber-600/10 p-4">
              <div className="flex items-center gap-2 mb-2">
                <svg
                  className="h-4 w-4 text-amber-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18"
                  />
                </svg>
                <span className="text-sm font-medium text-amber-300">
                  Hint Level {hintLevel}
                </span>
              </div>
              <p className="text-sm text-amber-200/80">{hint}</p>
            </div>
          )}

          {exercise.rubric ? (
            <MarkdownRenderer content={exercise.rubric} />
          ) : (
            <div className="text-slate-400 text-sm">
              <h2 className="text-lg font-semibold text-slate-100 mb-3">
                {exercise.title}
              </h2>
              <p>
                Complete the exercise in the code editor. Use the starter code
                as a starting point and refer to the lesson content for guidance.
              </p>
            </div>
          )}
        </div>

        {/* Right: Code editor + results */}
        <div className="flex w-1/2 flex-col gap-4 min-h-0">
          {/* Code editor */}
          <div className="flex-1 min-h-0 rounded-xl border border-slate-700/50 overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-700/50 bg-slate-800/50 px-4 py-2">
              <span className="text-xs font-medium text-slate-400">
                solution.{exercise.language === "python" ? "py" : exercise.language === "bash" ? "sh" : exercise.language === "javascript" ? "js" : exercise.language}
              </span>
              {submitting ? (
                <span className="text-xs text-amber-400 flex items-center gap-1.5">
                  <div className="h-3 w-3 animate-spin rounded-full border border-amber-400 border-t-transparent" />
                  Grading...
                </span>
              ) : (
                <span className="text-xs text-slate-500">{exercise.language}</span>
              )}
            </div>
            <CodeEditor
              value={code}
              onChange={(val) => setCode(val || "")}
              language={exercise.language}
              readOnly={submitting}
            />
          </div>

          {/* Results panel */}
          {result && (
            <div className="shrink-0 max-h-[40%] overflow-auto">
              <ExerciseResult result={result} attemptCount={attemptCount} />

              {/* Solution reveal gate — after N failed attempts */}
              {!result.passed && attemptCount >= SOLUTION_REVEAL_THRESHOLD && !showSolution && (
                <div className="mt-3 rounded-lg border border-purple-500/20 bg-purple-500/5 p-3">
                  <div className="flex items-start gap-2">
                    <svg className="h-4 w-4 shrink-0 text-purple-400 mt-0.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347" />
                    </svg>
                    <div>
                      <p className="text-sm text-purple-300 font-medium">
                        Stuck after {attemptCount} attempts?
                      </p>
                      <p className="text-xs text-purple-200/70 mt-1">
                        View the reference solution to learn from it. Study the approach, then try writing your own version.
                      </p>
                      <button
                        onClick={async () => {
                          try {
                            const sol = await fetchSolution(params.exerciseId);
                            setSolutionCode(sol);
                            setShowSolution(true);
                          } catch {
                            setSolutionCode("// Solution not available");
                            setShowSolution(true);
                          }
                        }}
                        className="mt-2 inline-flex items-center rounded-lg bg-purple-600/20 px-3 py-1.5 text-xs font-medium text-purple-300 hover:bg-purple-600/30 transition-colors"
                      >
                        <svg className="mr-1.5 h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                        </svg>
                        Learn from Solution
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Solution code viewer */}
              {showSolution && solutionCode && (
                <div className="mt-3 rounded-lg border border-purple-500/20 bg-slate-900/80 overflow-hidden">
                  <div className="flex items-center justify-between border-b border-purple-500/20 px-4 py-2 bg-purple-600/10">
                    <span className="text-xs font-medium text-purple-300">
                      Reference Solution — study the approach, then try your own version
                    </span>
                    <button
                      onClick={() => setShowSolution(false)}
                      className="text-xs text-slate-400 hover:text-slate-200"
                    >
                      Hide
                    </button>
                  </div>
                  <pre className="p-4 overflow-x-auto text-sm leading-6">
                    <code className="text-slate-300 font-mono">{solutionCode}</code>
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Chat panel */}
      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        lessonId={exercise.lessonId}
      />
    </div>
  );
}
