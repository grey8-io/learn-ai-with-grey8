const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

/* ------------------------------------------------------------------ */
/*  Manifest                                                          */
/* ------------------------------------------------------------------ */

export interface ManifestExercise {
  id: string;
  title: string;
  difficulty: string;
  starter_file: string;
  solution_file: string;
  test_file: string;
  rubric_file: string;
  hints: string[];
}

export interface ManifestLesson {
  id: string;
  title: string;
  phase: number;
  order: number;
  objectives: string[];
  prerequisites: string[];
  estimated_minutes: number;
  content_file: string;
  exercises: ManifestExercise[];
  quiz_file: string;
}

export interface ManifestPhase {
  phase: number;
  title: string;
  directory: string;
  lessons: ManifestLesson[];
}

export interface Manifest {
  title: string;
  version: string;
  schema: string;
  phases: ManifestPhase[];
}

/**
 * Fetch the full curriculum manifest.
 */
export async function fetchManifest(): Promise<Manifest> {
  const res = await fetch(`${API_BASE}/api/content/manifest`);
  if (!res.ok) {
    throw new Error(`Failed to fetch manifest: ${res.status}`);
  }
  return res.json();
}

/* ------------------------------------------------------------------ */
/*  Lessons                                                           */
/* ------------------------------------------------------------------ */

export interface LessonData {
  id: string;
  title: string;
  phaseId: string;
  content: string;
  exercises: { id: string; title: string; difficulty: string }[];
  objectives: string[];
  estimated_minutes: number;
  prerequisites: string[];
  prevLesson: string | null;
  nextLesson: string | null;
  hasQuiz: boolean;
}

/**
 * Fetch structured lesson data by encoded ID.
 * The lessonId should already use "--" encoding (e.g. "phase-01--lesson-01").
 */
export async function fetchLesson(lessonId: string): Promise<LessonData> {
  const res = await fetch(`${API_BASE}/api/content/lessons/${lessonId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch lesson: ${res.status}`);
  }
  return res.json();
}

/* ------------------------------------------------------------------ */
/*  Exercises                                                         */
/* ------------------------------------------------------------------ */

export interface ExerciseData {
  id: string;
  exerciseLocalId: string;
  title: string;
  difficulty: string;
  lessonId: string;
  lessonTitle: string;
  phaseId: string;
  starterCode: string;
  hints: string[];
  rubric: string;
  language: string;
  lessonContent: string;
}

/**
 * Fetch exercise data by encoded ID.
 * The exerciseId should use "--" encoding (e.g. "phase-01--lesson-01--ex-01").
 */
export async function fetchExercise(exerciseId: string): Promise<ExerciseData> {
  const res = await fetch(`${API_BASE}/api/content/exercises/${exerciseId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch exercise: ${res.status}`);
  }
  return res.json();
}

/**
 * Fetch the solution code for an exercise (for "Learn from Solution" after N attempts).
 */
export async function fetchSolution(exerciseId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/content/solution/${exerciseId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch solution: ${res.status}`);
  }
  const data = await res.json();
  return data.code;
}

/* ------------------------------------------------------------------ */
/*  Quizzes                                                           */
/* ------------------------------------------------------------------ */

export interface QuizQuestionData {
  question: string;
  options: string[];
  correct: number;
  explanation: string;
}

/**
 * Fetch quiz data by encoded lesson ID.
 * The quizId uses "--" encoding (e.g. "phase-01--lesson-01").
 */
export async function fetchQuiz(quizId: string): Promise<QuizQuestionData[]> {
  const res = await fetch(`${API_BASE}/api/content/quiz/${quizId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch quiz: ${res.status}`);
  }
  return res.json();
}

/* ------------------------------------------------------------------ */
/*  Grading                                                           */
/* ------------------------------------------------------------------ */

/**
 * Submit code for grading.
 * Returns score, pass/fail status, test results, and AI feedback.
 */
export async function submitCode(exerciseId: string, code: string) {
  const res = await fetch(`${API_BASE}/api/grade`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ exercise_id: exerciseId, code }),
  });
  if (!res.ok) {
    throw new Error(`Grading failed: ${res.status}`);
  }
  return res.json();
}

/* ------------------------------------------------------------------ */
/*  Hints                                                             */
/* ------------------------------------------------------------------ */

/**
 * Request a progressive hint for an exercise.
 * Level 1 = gentle nudge, Level 2 = more specific, Level 3 = near-solution.
 */
export async function getHint(
  exerciseId: string,
  code: string,
  level: number
) {
  const res = await fetch(`${API_BASE}/api/hint`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      exercise_id: exerciseId,
      code,
      hint_level: level,
    }),
  });
  if (!res.ok) {
    throw new Error(`Hint request failed: ${res.status}`);
  }
  return res.json();
}

/* ------------------------------------------------------------------ */
/*  Chat / Tutor                                                      */
/* ------------------------------------------------------------------ */

/**
 * Send a message to the AI tutor and get a streaming SSE response.
 * Returns a ReadableStream that the caller can consume for real-time display.
 */
export interface StudentProfilePayload {
  level?: string;
  streak_days?: number;
  lessons_completed?: number;
  total_lessons?: number;
  current_phase?: number;
  strong_topics?: string[];
  weak_topics?: string[];
  exercise_hint_avg?: number;
  exercise_attempts?: number;
}

export async function sendChatMessage(
  lessonId: string,
  message: string,
  history: { role: string; content: string }[],
  studentProfile?: StudentProfilePayload
): Promise<ReadableStream<Uint8Array>> {
  const res = await fetch(`${API_BASE}/api/tutor`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      type: "chat",
      lesson_id: lessonId,
      message,
      history,
      student_profile: studentProfile || null,
    }),
  });

  if (!res.ok) {
    throw new Error(`Chat request failed: ${res.status}`);
  }

  if (!res.body) {
    throw new Error("No response body for streaming");
  }

  return res.body;
}
