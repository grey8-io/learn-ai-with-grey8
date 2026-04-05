"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import QuizQuestion from "@/components/QuizQuestion";
import { fetchQuiz, QuizQuestionData } from "@/lib/api";
import { useProgress } from "@/components/ProgressProvider";
import { useGamification } from "@/components/GamificationProvider";
import type { QuizResult } from "@/lib/progress";

/** Extract phase number from a lesson/quiz URL id like "phase-01--lesson-01" */
function getPhaseNumber(id: string): number {
  const match = id.match(/phase-(\d+)/);
  return match ? parseInt(match[1], 10) : 0;
}

const PASS_PERCENT = 70;

/** Calculate the minimum correct answers needed to pass at 70%. */
function quizPassCount(total: number): number {
  return Math.ceil((PASS_PERCENT / 100) * total);
}

interface AnswerRecord {
  questionIndex: number;
  selectedOption: number;
  isCorrect: boolean;
}

export default function QuizPage({
  params,
}: {
  params: { quizId: string };
}) {
  const [questions, setQuestions] = useState<QuizQuestionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<AnswerRecord[]>([]);
  const [currentAnswered, setCurrentAnswered] = useState(false);
  const [finished, setFinished] = useState(false);
  const [previousBest, setPreviousBest] = useState<QuizResult | null>(null);
  const { backend, refreshStats } = useProgress();
  const { stats } = useProgress();
  const { onQuizComplete } = useGamification();

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchQuiz(params.quizId);
        setQuestions(data);
        const prev = await backend.getQuizResult(params.quizId);
        if (prev) setPreviousBest(prev);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load quiz"
        );
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [params.quizId, backend]);

  function handleAnswer(isCorrect: boolean, selectedOption: number) {
    setAnswers((prev) => [
      ...prev,
      { questionIndex: currentIndex, selectedOption, isCorrect },
    ]);
    setCurrentAnswered(true);
  }

  async function handleNext() {
    if (currentIndex + 1 >= questions.length) {
      setFinished(true);
      // Persist quiz result
      const allAnswers = [
        ...answers,
        // Include current answer (already added via handleAnswer)
      ];
      const correct = allAnswers.filter((a) => a.isCorrect).length;
      await backend.addQuizResult({
        quizId: params.quizId,
        answers: allAnswers.map((a) => ({
          questionIndex: a.questionIndex,
          selectedOption: a.selectedOption,
          correct: a.isCorrect,
        })),
        score: correct,
        completedAt: new Date().toISOString(),
      });

      // Auto-complete lesson if passing quiz
      if (correct >= quizPassCount(questions.length)) {
        const phaseNum = getPhaseNumber(params.quizId);
        const isEasyPhase = phaseNum >= 1 && phaseNum <= 3;
        const canonicalId = params.quizId.replace(/--/g, "/");

        if (isEasyPhase) {
          // Easy phases: quiz alone is enough
          await backend.upsertLessonProgress(canonicalId, "completed");
        } else {
          // Medium/hard phases: also need exercise passed
          // Exercise ID = lessonId--ex-01 (all lessons have one exercise)
          const exerciseId = `${params.quizId}--ex-01`;
          const bestSub = await backend.getBestSubmission(exerciseId);
          if (bestSub && (bestSub.score ?? 0) >= PASS_PERCENT) {
            await backend.upsertLessonProgress(canonicalId, "completed");
          }
        }
      }

      refreshStats();

      // Award XP
      onQuizComplete(correct, questions.length, stats?.currentStreakDays ?? 0);
    } else {
      setCurrentIndex((prev) => prev + 1);
      setCurrentAnswered(false);
    }
  }

  function handleRetake() {
    setCurrentIndex(0);
    setAnswers([]);
    setCurrentAnswered(false);
    setFinished(false);
  }

  const lessonId = params.quizId;
  const correctCount = answers.filter((a) => a.isCorrect).length;
  const totalCount = questions.length;
  const percentage = totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (error || questions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <h1 className="text-2xl font-bold text-slate-100">Quiz Not Found</h1>
        <p className="mt-2 text-sm text-slate-400">
          {error || "This lesson does not have a quiz yet."}
        </p>
        <Link href={`/learn/lessons/${lessonId}`} className="btn-primary mt-6">
          Back to Lesson
        </Link>
      </div>
    );
  }

  // Results screen
  if (finished) {
    return (
      <div className="mx-auto max-w-2xl space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <div
            className={`mx-auto flex h-16 w-16 items-center justify-center rounded-full ${
              percentage >= PASS_PERCENT
                ? "bg-emerald-600/20 text-emerald-400"
                : percentage >= 60
                ? "bg-amber-600/20 text-amber-400"
                : "bg-red-600/20 text-red-400"
            }`}
          >
            {percentage >= PASS_PERCENT ? (
              <svg
                className="h-8 w-8"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"
                />
              </svg>
            ) : (
              <svg
                className="h-8 w-8"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342"
                />
              </svg>
            )}
          </div>
          <h1 className="text-3xl font-bold text-slate-100">Quiz Complete</h1>
          <p className="text-lg text-slate-300">
            <span className="font-semibold text-white">{correctCount}/{totalCount}</span> correct
            {" "}
            <span
              className={`font-bold ${
                percentage >= PASS_PERCENT
                  ? "text-emerald-400"
                  : percentage >= 60
                  ? "text-amber-400"
                  : "text-red-400"
              }`}
            >
              — {percentage}%
            </span>
          </p>
        </div>

        {/* Summary */}
        <div className="card space-y-3">
          <h2 className="text-lg font-semibold text-slate-100">Summary</h2>
          <div className="space-y-2">
            {questions.map((q, i) => {
              const answer = answers[i];
              return (
                <div
                  key={i}
                  className={`flex items-start gap-3 rounded-lg border p-3 ${
                    answer?.isCorrect
                      ? "border-emerald-500/20 bg-emerald-500/5"
                      : "border-red-500/20 bg-red-500/5"
                  }`}
                >
                  <div
                    className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full ${
                      answer?.isCorrect
                        ? "bg-emerald-600 text-white"
                        : "bg-red-600 text-white"
                    }`}
                  >
                    {answer?.isCorrect ? (
                      <svg
                        className="h-3 w-3"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={3}
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="m4.5 12.75 6 6 9-13.5"
                        />
                      </svg>
                    ) : (
                      <svg
                        className="h-3 w-3"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={3}
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M6 18 18 6M6 6l12 12"
                        />
                      </svg>
                    )}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-200">
                      {q.question}
                    </p>
                    {!answer?.isCorrect && (
                      <p className="mt-1 text-xs text-slate-400">
                        Correct answer: {q.options[q.correct]}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Passing message */}
        {percentage >= PASS_PERCENT && (
          <div className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
            <svg className="h-5 w-5 text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
            <span className="text-sm font-medium text-emerald-300">
              Quiz passed! Your lesson progress has been updated.
            </span>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-center gap-4">
          {percentage < PASS_PERCENT ? (
            <button onClick={handleRetake} className="btn-secondary">
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
                  d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182"
                />
              </svg>
              Try Again
            </button>
          ) : (
            <button onClick={handleRetake} className="btn-secondary">
              Retake Quiz
            </button>
          )}
          <Link href={`/learn/lessons/${lessonId}`} className="btn-primary">
            Back to Lesson
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
        </div>
      </div>
    );
  }

  // Question screen
  const currentQuestion = questions[currentIndex];

  return (
    <div className="mx-auto max-w-2xl space-y-8">
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
          href={`/learn/lessons/${lessonId}`}
          className="hover:text-primary-400 transition-colors"
        >
          Lesson
        </Link>
        <span>/</span>
        <span className="text-slate-200">Quiz</span>
        {previousBest && (
          <span className="ml-auto text-xs text-slate-500">
            Previous best: {previousBest.score}/{questions.length}
          </span>
        )}
      </nav>

      {/* Quiz card */}
      <div className="card">
        <QuizQuestion
          key={currentIndex}
          question={currentQuestion.question}
          options={currentQuestion.options}
          correct={currentQuestion.correct}
          explanation={currentQuestion.explanation}
          questionNumber={currentIndex + 1}
          totalQuestions={questions.length}
          onAnswer={handleAnswer}
        />

        {/* Next button */}
        {currentAnswered && (
          <div className="mt-6 flex justify-end">
            <button onClick={handleNext} className="btn-primary">
              {currentIndex + 1 >= questions.length
                ? "See Results"
                : "Next Question"}
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
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
