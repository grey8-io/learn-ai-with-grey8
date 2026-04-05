import { createServerClient as createSSRServerClient, type CookieOptions } from "@supabase/ssr";
import { cookies } from "next/headers";
import type { Database } from "./supabase";

/**
 * Cookie-aware Supabase client for Server Components, Server Actions, and Route Handlers.
 * Reads the session from request cookies so getUser() works server-side.
 */
export async function createSupabaseServerClient() {
  const cookieStore = await cookies();

  return createSSRServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet: { name: string; value: string; options: CookieOptions }[]) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // setAll can fail in Server Components (read-only).
            // This is fine — the middleware refreshes the session.
          }
        },
      },
    }
  );
}
