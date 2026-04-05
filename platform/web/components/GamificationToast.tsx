"use client";

import { useEffect, useState } from "react";

export interface ToastData {
  id: string;
  type: "xp" | "achievement" | "level_up" | "streak";
  title: string;
  subtitle?: string;
  icon: string;
}

interface GamificationToastProps {
  toasts: ToastData[];
  onDismiss: (id: string) => void;
}

export default function GamificationToast({ toasts, onDismiss }: GamificationToastProps) {
  return (
    <div className="fixed top-4 right-4 z-[90] flex flex-col gap-3 pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onDismiss }: { toast: ToastData; onDismiss: (id: string) => void }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Animate in
    requestAnimationFrame(() => setVisible(true));
    // Auto-dismiss
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(() => onDismiss(toast.id), 300);
    }, 4000);
    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  const bgColor = {
    xp: "from-primary-600/90 to-primary-700/90",
    achievement: "from-amber-600/90 to-amber-700/90",
    level_up: "from-purple-600/90 to-purple-700/90",
    streak: "from-rose-600/90 to-rose-700/90",
  }[toast.type];

  return (
    <div
      className={`pointer-events-auto flex items-center gap-3 rounded-xl bg-gradient-to-r ${bgColor} backdrop-blur-sm px-5 py-3 shadow-2xl border border-white/10 transition-all duration-300 ${
        visible ? "translate-x-0 opacity-100" : "translate-x-full opacity-0"
      }`}
    >
      <span className="text-2xl">{toast.icon}</span>
      <div>
        <p className="text-sm font-bold text-white">{toast.title}</p>
        {toast.subtitle && (
          <p className="text-xs text-white/70">{toast.subtitle}</p>
        )}
      </div>
    </div>
  );
}
