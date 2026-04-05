import { NextRequest, NextResponse } from "next/server";
import { createSupabaseMiddlewareClient } from "@/lib/supabase-middleware";
import { isSupabaseConfigured } from "@/lib/supabase";

export async function middleware(request: NextRequest) {
  const response = NextResponse.next({ request });

  // If Supabase is not configured, skip all auth checks — let everyone through
  if (!isSupabaseConfigured()) {
    return response;
  }

  const supabase = createSupabaseMiddlewareClient(request, response);

  // Refresh session — this keeps the cookie alive
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // /learn/* routes are open to everyone — progress uses localStorage for
  // anonymous users and Supabase for signed-in users.

  // Redirect authenticated users away from auth pages
  if (user && request.nextUrl.pathname.startsWith("/auth")) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return response;
}

export const config = {
  matcher: ["/learn/:path*", "/auth/:path*"],
};
