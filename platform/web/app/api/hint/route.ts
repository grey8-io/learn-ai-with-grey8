import { NextRequest } from "next/server";
import { tutorIdentityHeaders } from "@/lib/tutor-identity";

const TUTOR_URL = process.env.NEXT_PUBLIC_TUTOR_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const identity = await tutorIdentityHeaders();

    const response = await fetch(`${TUTOR_URL}/hint`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...identity },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      // Forward the tutor's specific error (401 sign-in, 429 quota, 503 breaker).
      const err = await response
        .json()
        .catch(() => ({ error: "Hint service unavailable" }));
      return Response.json(err, { status: response.status });
    }

    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    console.error("Hint API error:", error);
    return Response.json(
      { error: "Failed to connect to hint service" },
      { status: 503 }
    );
  }
}
