"use client";

import { useEffect, useState } from "react";

interface ConfettiProps {
  active: boolean;
  duration?: number;
}

interface Particle {
  id: number;
  x: number;
  color: string;
  delay: number;
  size: number;
  drift: number;
}

const COLORS = [
  "#818cf8", // indigo
  "#2dd4bf", // teal
  "#fbbf24", // amber
  "#fb7185", // rose
  "#34d399", // emerald
  "#a78bfa", // purple
  "#60a5fa", // blue
];

export default function Confetti({ active, duration = 3000 }: ConfettiProps) {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    if (!active) {
      setParticles([]);
      return;
    }

    const newParticles: Particle[] = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      delay: Math.random() * 500,
      size: Math.random() * 6 + 4,
      drift: (Math.random() - 0.5) * 40,
    }));
    setParticles(newParticles);

    const timer = setTimeout(() => setParticles([]), duration);
    return () => clearTimeout(timer);
  }, [active, duration]);

  if (particles.length === 0) return null;

  return (
    <div className="fixed inset-0 z-[100] pointer-events-none overflow-hidden">
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute animate-confetti-fall"
          style={{
            left: `${p.x}%`,
            top: "-10px",
            width: `${p.size}px`,
            height: `${p.size}px`,
            backgroundColor: p.color,
            borderRadius: Math.random() > 0.5 ? "50%" : "2px",
            animationDelay: `${p.delay}ms`,
            animationDuration: `${1500 + Math.random() * 1000}ms`,
            ["--drift" as string]: `${p.drift}px`,
          }}
        />
      ))}
    </div>
  );
}
