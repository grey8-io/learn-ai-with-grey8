"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { signIn } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") || "/";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { error: authError } = await signIn(email, password);
    if (authError) {
      setError(authError.message);
      setLoading(false);
      return;
    }

    router.push(redirect);
    router.refresh();
  }

  return (
    <div className="card">
      <div className="mb-6 text-center">
        <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 text-white font-bold text-lg">
          AI
        </div>
        <h1 className="text-xl font-bold text-slate-100">Welcome back</h1>
        <p className="mt-1 text-sm text-slate-400">
          Sign in to continue learning
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="email"
            className="mb-1 block text-sm font-medium text-slate-300"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
            placeholder="you@example.com"
            required
          />
        </div>

        <div>
          <label
            htmlFor="password"
            className="mb-1 block text-sm font-medium text-slate-300"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
            placeholder="Your password"
            required
            minLength={6}
          />
        </div>

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 px-3 py-2 text-sm text-red-400">
            {error}
          </div>
        )}

        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-slate-400">
        Don&apos;t have an account?{" "}
        <Link
          href="/auth/register"
          className="font-medium text-primary-400 hover:text-primary-300"
        >
          Sign up
        </Link>
      </p>
    </div>
  );
}
