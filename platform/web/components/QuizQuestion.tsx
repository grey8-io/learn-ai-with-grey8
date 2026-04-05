"use client";

import { useState } from "react";

export interface QuizQuestionProps {
  question: string;
  options: string[];
  correct: number;
  explanation: string;
  questionNumber: number;
  totalQuestions: number;
  onAnswer: (isCorrect: boolean, selectedOption: number) => void;
}

const OPTION_LABELS = ["A", "B", "C", "D"];

export default function QuizQuestion({
  question,
  options,
  correct,
  explanation,
  questionNumber,
  totalQuestions,
  onAnswer,
}: QuizQuestionProps) {
  const [selected, setSelected] = useState<number | null>(null);
  const answered = selected !== null;

  function handleSelect(index: number) {
    if (answered) return;
    setSelected(index);
    onAnswer(index === correct, index);
  }

  return (
    <div className="space-y-6">
      {/* Progress indicator */}
      <div className="flex items-center justify-between text-sm text-slate-400">
        <span>
          Question {questionNumber} of {totalQuestions}
        </span>
        <div className="flex gap-1">
          {Array.from({ length: totalQuestions }, (_, i) => (
            <div
              key={i}
              className={`h-1.5 w-6 rounded-full transition-colors ${
                i < questionNumber - 1
                  ? "bg-primary-500"
                  : i === questionNumber - 1
                  ? "bg-primary-400"
                  : "bg-slate-700"
              }`}
            />
          ))}
        </div>
      </div>

      {/* Question */}
      <h2 className="text-xl font-semibold text-slate-100 leading-relaxed">
        {question}
      </h2>

      {/* Options */}
      <div className="space-y-3">
        {options.map((option, index) => {
          let borderClass = "border-slate-700/50 hover:border-slate-500";
          let bgClass = "bg-surface-800";
          let labelBg = "bg-slate-700 text-slate-300";

          if (answered) {
            if (index === correct) {
              borderClass = "border-emerald-500";
              bgClass = "bg-emerald-500/10";
              labelBg = "bg-emerald-600 text-white";
            } else if (index === selected) {
              borderClass = "border-red-500";
              bgClass = "bg-red-500/10";
              labelBg = "bg-red-600 text-white";
            } else {
              borderClass = "border-slate-700/30";
              bgClass = "bg-surface-800 opacity-50";
            }
          }

          return (
            <button
              key={index}
              onClick={() => handleSelect(index)}
              disabled={answered}
              className={`flex w-full items-center gap-4 rounded-xl border p-4 text-left transition-all ${borderClass} ${bgClass} ${
                !answered
                  ? "cursor-pointer hover:bg-surface-700 active:scale-[0.99]"
                  : "cursor-default"
              }`}
            >
              <span
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm font-bold transition-colors ${labelBg}`}
              >
                {OPTION_LABELS[index]}
              </span>
              <span className="text-sm font-medium text-slate-200">
                {option}
              </span>
              {answered && index === correct && (
                <svg
                  className="ml-auto h-5 w-5 shrink-0 text-emerald-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="m4.5 12.75 6 6 9-13.5"
                  />
                </svg>
              )}
              {answered && index === selected && index !== correct && (
                <svg
                  className="ml-auto h-5 w-5 shrink-0 text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18 18 6M6 6l12 12"
                  />
                </svg>
              )}
            </button>
          );
        })}
      </div>

      {/* Explanation */}
      {answered && (
        <div
          className={`rounded-xl border p-4 ${
            selected === correct
              ? "border-emerald-500/30 bg-emerald-500/5"
              : "border-amber-500/30 bg-amber-500/5"
          }`}
        >
          <div className="flex items-start gap-3">
            <div
              className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${
                selected === correct
                  ? "bg-emerald-600/20 text-emerald-400"
                  : "bg-amber-600/20 text-amber-400"
              }`}
            >
              {selected === correct ? (
                <svg
                  className="h-3.5 w-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.5}
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
                  className="h-3.5 w-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 18v.01M12 6v6"
                  />
                </svg>
              )}
            </div>
            <div>
              <p
                className={`text-sm font-semibold ${
                  selected === correct ? "text-emerald-300" : "text-amber-300"
                }`}
              >
                {selected === correct ? "Correct!" : "Not quite"}
              </p>
              <p className="mt-1 text-sm leading-relaxed text-slate-300">
                {explanation}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
