import { NextRequest } from "next/server";
import { tutorIdentityHeaders } from "@/lib/tutor-identity";

const TUTOR_URL = process.env.NEXT_PUBLIC_TUTOR_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const identity = await tutorIdentityHeaders();

    const response = await fetch(`${TUTOR_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...identity },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      // Forward the tutor's specific error (401 sign-in, 429 quota, 503 breaker)
      // so the UI can show the real message instead of a generic failure.
      const err = await response
        .json()
        .catch(() => ({ error: "Tutor service unavailable" }));
      return Response.json(err, { status: response.status });
    }

    // Stream the SSE response through
    if (response.headers.get("content-type")?.includes("text/event-stream")) {
      return new Response(response.body, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
        },
      });
    }

    // Fall back to JSON response
    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    console.error("Tutor API error:", error);
    return Response.json(
      { error: "Failed to connect to tutor service" },
      { status: 503 }
    );
  }
}
