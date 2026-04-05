import { NextRequest } from "next/server";
import { readFile, stat } from "fs/promises";
import { join } from "path";

const CURRICULUM_DIR =
  process.env.CURRICULUM_DIR ||
  join(process.cwd(), "..", "..", "curriculum");

interface ManifestExercise {
  id: string;
  title: string;
  difficulty: string;
  starter_file: string;
  solution_file: string;
  test_file: string;
  rubric_file: string;
  hints: string[];
}

interface ManifestLesson {
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

interface ManifestPhase {
  phase: number;
  title: string;
  directory: string;
  lessons: ManifestLesson[];
}

interface Manifest {
  title: string;
  version: string;
  schema: string;
  phases: ManifestPhase[];
}

let _manifestCache: Manifest | null = null;
let _manifestMtime: number = 0;

async function readManifest(): Promise<Manifest> {
  const manifestPath = join(CURRICULUM_DIR, "manifest.json");
  // In dev, check mtime to bust cache on edits; in prod, cache indefinitely
  if (_manifestCache) {
    if (process.env.NODE_ENV === "production") return _manifestCache;
    try {
      const s = await stat(manifestPath);
      if (s.mtimeMs === _manifestMtime) return _manifestCache;
    } catch {
      // stat failed, re-read
    }
  }
  const raw = await readFile(manifestPath, "utf-8");
  const manifest = JSON.parse(raw);
  try {
    const s = await stat(manifestPath);
    _manifestMtime = s.mtimeMs;
  } catch {
    // ignore
  }
  _manifestCache = manifest;
  return manifest;
}

function getAllLessons(manifest: Manifest): ManifestLesson[] {
  const lessons: ManifestLesson[] = [];
  for (const phase of manifest.phases) {
    for (const lesson of phase.lessons) {
      lessons.push(lesson);
    }
  }
  return lessons;
}

async function readFileSafe(filePath: string): Promise<string | null> {
  try {
    return await readFile(filePath, "utf-8");
  } catch {
    return null;
  }
}

async function handleLessonRequest(lessonId: string): Promise<Response> {
  // lessonId comes in as "phase-01--lesson-01", decode to "phase-01/lesson-01"
  const decodedId = lessonId.replace(/--/g, "/");
  const manifest = await readManifest();
  const allLessons = getAllLessons(manifest);

  const lessonIndex = allLessons.findIndex((l) => l.id === decodedId);
  if (lessonIndex === -1) {
    return Response.json({ error: "Lesson not found" }, { status: 404 });
  }

  const lesson = allLessons[lessonIndex];
  const prevLesson = lessonIndex > 0 ? allLessons[lessonIndex - 1] : null;
  const nextLesson =
    lessonIndex < allLessons.length - 1 ? allLessons[lessonIndex + 1] : null;

  // Read the content markdown file
  let content = "";
  if (lesson.content_file) {
    const contentPath = join(CURRICULUM_DIR, lesson.content_file);
    content = (await readFileSafe(contentPath)) || `# ${lesson.title}\n\nContent coming soon.`;
  }

  // Encode exercise IDs for URL usage: "phase-01/lesson-01" + "ex-01" -> "phase-01--lesson-01--ex-01"
  const encodedLessonId = lesson.id.replace(/\//g, "--");
  const exercises = lesson.exercises.map((ex) => ({
    id: `${encodedLessonId}--${ex.id}`,
    title: ex.title,
    difficulty: ex.difficulty,
  }));

  const phaseId = String(lesson.phase);

  return Response.json({
    id: encodedLessonId,
    title: lesson.title,
    phaseId,
    content,
    exercises,
    objectives: lesson.objectives,
    estimated_minutes: lesson.estimated_minutes,
    prerequisites: lesson.prerequisites,
    prevLesson: prevLesson ? prevLesson.id.replace(/\//g, "--") : null,
    nextLesson: nextLesson ? nextLesson.id.replace(/\//g, "--") : null,
    hasQuiz: !!lesson.quiz_file,
  });
}

async function handleExerciseRequest(encodedId: string): Promise<Response> {
  // encodedId is like "phase-01--lesson-01--ex-01"
  // Split on "--" to get parts: ["phase-01", "lesson-01", "ex-01"]
  const parts = encodedId.split("--");
  if (parts.length < 3) {
    return Response.json({ error: "Invalid exercise ID format" }, { status: 400 });
  }

  const exerciseLocalId = parts[parts.length - 1]; // e.g. "ex-01"
  const lessonId = parts.slice(0, parts.length - 1).join("/"); // e.g. "phase-01/lesson-01"

  const manifest = await readManifest();
  const allLessons = getAllLessons(manifest);
  const lesson = allLessons.find((l) => l.id === lessonId);
  if (!lesson) {
    return Response.json({ error: "Lesson not found" }, { status: 404 });
  }

  const exercise = lesson.exercises.find((ex) => ex.id === exerciseLocalId);
  if (!exercise) {
    return Response.json({ error: "Exercise not found" }, { status: 404 });
  }

  // Read starter code
  const starterCode = exercise.starter_file
    ? await readFileSafe(join(CURRICULUM_DIR, exercise.starter_file))
    : null;

  // Read rubric
  const rubric = exercise.rubric_file
    ? await readFileSafe(join(CURRICULUM_DIR, exercise.rubric_file))
    : null;

  // Read lesson content for instructions context
  const lessonContent = lesson.content_file
    ? await readFileSafe(join(CURRICULUM_DIR, lesson.content_file))
    : null;

  // Determine the language from the starter file extension
  const ext = exercise.starter_file?.split(".").pop() || "py";
  const languageMap: Record<string, string> = {
    py: "python",
    js: "javascript",
    ts: "typescript",
    sh: "bash",
    bash: "bash",
  };
  const language = languageMap[ext] || ext;

  const encodedLessonId = lessonId.replace(/\//g, "--");

  return Response.json({
    id: encodedId,
    exerciseLocalId: exerciseLocalId,
    title: exercise.title,
    difficulty: exercise.difficulty,
    lessonId: encodedLessonId,
    lessonTitle: lesson.title,
    phaseId: String(lesson.phase),
    starterCode: starterCode || "# Write your solution here\n",
    hints: exercise.hints,
    rubric: rubric || "",
    language,
    lessonContent: lessonContent || "",
  });
}

async function handleSolutionRequest(encodedId: string): Promise<Response> {
  // encodedId is like "phase-01--lesson-01--ex-01"
  const parts = encodedId.split("--");
  if (parts.length < 3) {
    return Response.json({ error: "Invalid exercise ID format" }, { status: 400 });
  }

  const exerciseLocalId = parts[parts.length - 1];
  const lessonId = parts.slice(0, parts.length - 1).join("/");

  const manifest = await readManifest();
  const allLessons = getAllLessons(manifest);
  const lesson = allLessons.find((l) => l.id === lessonId);
  if (!lesson) {
    return Response.json({ error: "Lesson not found" }, { status: 404 });
  }

  const exercise = lesson.exercises.find((ex) => ex.id === exerciseLocalId);
  if (!exercise) {
    return Response.json({ error: "Exercise not found" }, { status: 404 });
  }

  const solutionCode = exercise.solution_file
    ? await readFileSafe(join(CURRICULUM_DIR, exercise.solution_file))
    : null;

  if (!solutionCode) {
    return Response.json({ error: "Solution not available" }, { status: 404 });
  }

  return Response.json({ code: solutionCode });
}

async function handleQuizRequest(encodedId: string): Promise<Response> {
  // encodedId is like "phase-01--lesson-01", decode to "phase-01/lesson-01"
  const decodedId = encodedId.replace(/--/g, "/");
  const manifest = await readManifest();
  const allLessons = getAllLessons(manifest);

  const lesson = allLessons.find((l) => l.id === decodedId);
  if (!lesson) {
    return Response.json({ error: "Lesson not found" }, { status: 404 });
  }

  if (!lesson.quiz_file) {
    return Response.json({ error: "No quiz for this lesson" }, { status: 404 });
  }

  const quizPath = join(CURRICULUM_DIR, lesson.quiz_file);
  const quizContent = await readFileSafe(quizPath);
  if (!quizContent) {
    return Response.json({ error: "Quiz file not found" }, { status: 404 });
  }

  return Response.json(JSON.parse(quizContent));
}

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const pathParts = params.path;

    // Route: /api/content/manifest -> return full manifest
    if (pathParts.length === 1 && pathParts[0] === "manifest") {
      const manifest = await readManifest();
      return Response.json(manifest);
    }

    // Route: /api/content/lessons/{encodedLessonId}
    // e.g. /api/content/lessons/phase-01--lesson-01
    if (pathParts.length === 2 && pathParts[0] === "lessons") {
      return handleLessonRequest(pathParts[1]);
    }

    // Route: /api/content/exercises/{encodedExerciseId}
    // e.g. /api/content/exercises/phase-01--lesson-01--ex-01
    if (pathParts.length === 2 && pathParts[0] === "exercises") {
      return handleExerciseRequest(pathParts[1]);
    }

    // Route: /api/content/quiz/{encodedLessonId}
    // e.g. /api/content/quiz/phase-01--lesson-01
    if (pathParts.length === 2 && pathParts[0] === "quiz") {
      return handleQuizRequest(pathParts[1]);
    }

    // Route: /api/content/solution/{encodedExerciseId}
    // Returns the solution code for "Learn from Solution" feature
    if (pathParts.length === 2 && pathParts[0] === "solution") {
      return handleSolutionRequest(pathParts[1]);
    }

    // Fallback: serve raw files from curriculum directory
    const filePath = join(CURRICULUM_DIR, ...pathParts);

    // Security: prevent directory traversal
    if (!filePath.startsWith(CURRICULUM_DIR)) {
      return Response.json({ error: "Invalid path" }, { status: 400 });
    }

    const content = await readFile(filePath, "utf-8");

    // Return markdown as-is, JSON parsed
    if (filePath.endsWith(".json")) {
      return Response.json(JSON.parse(content));
    }

    if (filePath.endsWith(".md")) {
      return new Response(content, {
        headers: { "Content-Type": "text/markdown; charset=utf-8" },
      });
    }

    return new Response(content, {
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  } catch (error: unknown) {
    if (
      error &&
      typeof error === "object" &&
      "code" in error &&
      error.code === "ENOENT"
    ) {
      return Response.json({ error: "Content not found" }, { status: 404 });
    }
    console.error("Content API error:", error);
    return Response.json(
      { error: "Failed to read content" },
      { status: 500 }
    );
  }
}
