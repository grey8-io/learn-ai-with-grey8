import { NextRequest } from "next/server";

const TUTOR_URL = process.env.NEXT_PUBLIC_TUTOR_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${TUTOR_URL}/hint`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return Response.json(
        { error: "Hint service unavailable" },
        { status: response.status }
      );
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
