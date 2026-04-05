import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase-server";

/**
 * Handles the OAuth / email-confirmation callback from Supabase Auth.
 * Exchanges the one-time code for a session cookie, then redirects home.
 */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") || "/";

  if (code) {
    const supabase = await createSupabaseServerClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      return NextResponse.redirect(new URL(next, origin));
    }
  }

  // If code exchange fails, redirect to login with error hint
  return NextResponse.redirect(new URL("/auth/login", origin));
}
