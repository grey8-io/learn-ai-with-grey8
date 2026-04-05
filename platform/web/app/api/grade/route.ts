import { NextRequest } from "next/server";

const TUTOR_URL = process.env.NEXT_PUBLIC_TUTOR_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${TUTOR_URL}/grade`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return Response.json(
        { error: "Grading service unavailable" },
        { status: response.status }
      );
    }

    const data = await response.json();
    // Map snake_case backend fields to camelCase frontend fields
    return Response.json({
      score: data.score,
      passed: data.passed,
      tests: data.test_results ?? data.tests ?? [],
      feedback: data.feedback ?? "",
    });
  } catch (error) {
    console.error("Grade API error:", error);
    return Response.json(
      {
        score: 0,
        passed: false,
        tests: [],
        feedback: "Grading service is currently unavailable. Please try again later.",
      },
      { status: 503 }
    );
  }
}
