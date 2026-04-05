"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

const navItems = [
  {
    label: "Dashboard",
    href: "/",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
      </svg>
    ),
  },
  {
    label: "Phases",
    href: "/learn/phases",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
      </svg>
    ),
  },
  {
    label: "Projects",
    href: "/projects",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
      </svg>
    ),
  },
];

export default function Navigation() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, loading, signOut } = useAuth();

  // Hide sidebar on auth pages
  if (pathname.startsWith("/auth")) return null;

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed left-4 top-4 z-50 flex h-10 w-10 items-center justify-center rounded-lg bg-surface-800 border border-slate-700/50 text-slate-300 lg:hidden"
        aria-label="Toggle navigation"
      >
        {mobileOpen ? (
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        )}
      </button>

      {/* Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-slate-700/50 bg-surface-900 transition-transform lg:static lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Logo */}
        <div className="flex h-16 items-center gap-3 border-b border-slate-700/50 px-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 text-white font-bold text-sm">
            AI
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-100">Learn AI</h1>
            <p className="text-xs text-slate-500">With Grey8</p>
          </div>
        </div>

        {/* Nav links */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-primary-600/15 text-primary-300"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`}
              >
                {item.icon}
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="border-t border-slate-700/50 p-4">
          {loading ? (
            <div className="animate-pulse rounded-lg bg-slate-800/50 p-3">
              <div className="h-4 w-24 rounded bg-slate-700" />
              <div className="mt-2 h-3 w-32 rounded bg-slate-700" />
            </div>
          ) : user ? (
            <div className="rounded-lg bg-slate-800/50 p-3">
              <p className="text-sm font-semibold text-slate-200 truncate">
                {user.user_metadata?.display_name || user.email?.split("@")[0]}
              </p>
              <p className="mt-0.5 text-xs text-slate-500 truncate">
                {user.email}
              </p>
              <button
                onClick={signOut}
                className="mt-2 w-full rounded-md bg-slate-700/50 px-2 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-700 transition-colors"
              >
                Sign out
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-xs text-slate-500 mb-2">
                Progress saved locally
              </p>
              <Link
                href="/auth/login"
                className="btn-primary w-full text-center text-xs"
              >
                Sign in to sync
              </Link>
              <Link
                href="/auth/register"
                className="btn-secondary w-full text-center text-xs"
              >
                Create account
              </Link>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
