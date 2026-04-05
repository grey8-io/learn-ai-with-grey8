/** Shared types for the progress persistence layer. */

export interface LessonStatus {
  lessonId: string;
  status: "not_started" | "in_progress" | "completed";
  startedAt?: string;
  completedAt?: string;
}

export interface Submission {
  exerciseId: string;
  code: string;
  score: number | null;
  testPassed: boolean | null;
  testResults: unknown;
  rubricScore: number | null;
  rubricFeedback: string | null;
  submittedAt: string;
}

export interface QuizAnswer {
  questionIndex: number;
  selectedOption: number;
  correct: boolean;
}

export interface QuizResult {
  quizId: string;
  answers: QuizAnswer[];
  score: number;
  completedAt: string;
}

export interface ChatMessage {
  lessonId: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
}

export interface ProgressStats {
  lessonsCompleted: number;
  lessonsInProgress: number;
  exercisesPassed: number;
  totalSubmissions: number;
  quizzesCompleted: number;
  currentStreakDays: number;
  lastActiveDate: string | null;
}

export interface ExportedData {
  lessons: LessonStatus[];
  submissions: Submission[];
  quizzes: QuizResult[];
  chats: Record<string, ChatMessage[]>;
}

/**
 * Backend interface for progress persistence.
 * Both localStorage and Supabase backends implement this.
 */
export interface ProgressBackend {
  // Lessons
  getLessonProgress(lessonId: string): Promise<LessonStatus | null>;
  getAllLessonProgress(): Promise<LessonStatus[]>;
  upsertLessonProgress(
    lessonId: string,
    status: "in_progress" | "completed"
  ): Promise<void>;

  // Submissions
  addSubmission(submission: Submission): Promise<void>;
  getSubmissions(exerciseId: string): Promise<Submission[]>;
  getBestSubmission(exerciseId: string): Promise<Submission | null>;

  // Quizzes
  addQuizResult(result: QuizResult): Promise<void>;
  getQuizResult(quizId: string): Promise<QuizResult | null>;

  // Chat
  getChatMessages(lessonId: string): Promise<ChatMessage[]>;
  addChatMessages(messages: ChatMessage[]): Promise<void>;
  clearChatMessages(lessonId: string): Promise<void>;

  // Stats
  getStats(): Promise<ProgressStats>;

  // Migration support (localStorage only)
  exportAll?(): ExportedData;
  clearAll?(): void;
}
