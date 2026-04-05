"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { sendChatMessage, type StudentProfilePayload } from "@/lib/api";
import { useProgress } from "@/components/ProgressProvider";
import { useGamification } from "@/components/GamificationProvider";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatPanelProps {
  open: boolean;
  onClose: () => void;
  lessonId: string;
}

const GREETING: Message = {
  role: "assistant",
  content:
    "Hi! I'm your AI tutor. Ask me anything about this lesson or exercise. I'll guide you without giving away the answer directly.",
};

export default function ChatPanel({ open, onClose, lessonId }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([GREETING]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { backend, stats } = useProgress();
  const { level, state: gamState } = useGamification();

  /** Build a lightweight student profile from current progress + gamification state. */
  const buildProfile = useCallback((): StudentProfilePayload => {
    const phaseMatch = lessonId.match(/phase-(\d+)/);
    const currentPhase = phaseMatch ? parseInt(phaseMatch[1], 10) : 1;
    return {
      level: `${level.title} (${gamState.totalXP} XP)`,
      streak_days: stats?.currentStreakDays ?? 0,
      lessons_completed: stats?.lessonsCompleted ?? 0,
      total_lessons: 35,
      current_phase: currentPhase,
      exercise_attempts: stats?.totalSubmissions ?? 0,
      exercise_hint_avg: stats?.totalSubmissions
        ? Object.values(gamState.hintsUsedPerExercise).reduce((a, b) => a + b, 0) /
          Math.max(Object.keys(gamState.hintsUsedPerExercise).length, 1)
        : 0,
    };
  }, [lessonId, level, gamState, stats]);

  // Load saved chat history when panel opens
  useEffect(() => {
    if (!open || historyLoaded) return;
    backend.getChatMessages(lessonId).then((saved) => {
      if (saved.length > 0) {
        setMessages([
          GREETING,
          ...saved.map((m) => ({ role: m.role, content: m.content })),
        ]);
      }
      setHistoryLoaded(true);
    });
  }, [open, lessonId, backend, historyLoaded]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || streaming) return;

    const userMessage = input.trim();
    setInput("");

    const newMessages: Message[] = [
      ...messages,
      { role: "user", content: userMessage },
    ];
    setMessages(newMessages);
    setStreaming(true);

    // Add placeholder assistant message
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const stream = await sendChatMessage(
        lessonId,
        userMessage,
        newMessages.slice(0, -1), // history without the latest user msg
        buildProfile()
      );

      const reader = stream.getReader();
      const decoder = new TextDecoder();
      let accumulated = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") continue;
            try {
              const parsed = JSON.parse(data);
              accumulated += parsed.content || parsed.text || "";
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: "assistant",
                  content: accumulated,
                };
                return updated;
              });
            } catch {
              // Non-JSON SSE data, treat as plain text
              accumulated += data;
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: "assistant",
                  content: accumulated,
                };
                return updated;
              });
            }
          }
        }
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content:
            "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        };
        return updated;
      });
    } finally {
      setStreaming(false);
      // Persist the user message and assistant response
      setMessages((prev) => {
        const lastAssistant = prev[prev.length - 1];
        if (lastAssistant?.content) {
          const now = new Date().toISOString();
          backend.addChatMessages([
            { lessonId, role: "user", content: userMessage, createdAt: now },
            {
              lessonId,
              role: "assistant",
              content: lastAssistant.content,
              createdAt: now,
            },
          ]);
        }
        return prev;
      });
    }
  }

  async function handleClearChat() {
    await backend.clearChatMessages(lessonId);
    setMessages([GREETING]);
    setHistoryLoaded(false);
  }

  return (
    <>
      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/30"
          onClick={onClose}
        />
      )}

      {/* Panel */}
      <div
        className={`fixed inset-y-0 right-0 z-50 flex w-96 flex-col border-l border-slate-700/50 bg-surface-900 shadow-2xl transition-transform duration-300 ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-700/50 px-4 py-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-600/20 text-primary-400">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                AI Tutor
              </h3>
              <p className="text-xs text-slate-500">Ask me anything</p>
            </div>
          </div>
          <button
            onClick={handleClearChat}
            title="Clear chat history"
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-auto px-4 py-4 space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
                  msg.role === "user"
                    ? "bg-primary-600 text-white rounded-br-md"
                    : "bg-slate-800 text-slate-200 rounded-bl-md"
                }`}
              >
                {msg.content || (
                  <div className="flex items-center gap-1">
                    <div className="h-2 w-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="h-2 w-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="h-2 w-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-slate-700/50 p-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask your tutor..."
              disabled={streaming}
              className="input flex-1"
            />
            <button
              type="submit"
              disabled={!input.trim() || streaming}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-600 text-white transition-colors hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
