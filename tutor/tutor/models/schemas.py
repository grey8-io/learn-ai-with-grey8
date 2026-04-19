"""Pydantic models for the tutor engine API."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class StudentProfile(BaseModel):
    """Lightweight student profile for personalized tutor responses."""
    level: str = ""            # e.g. "Builder (600 XP)"
    streak_days: int = 0
    lessons_completed: int = 0
    total_lessons: int = 35
    current_phase: int = 1
    strong_topics: list[str] = Field(default_factory=list)   # e.g. ["Python basics", "Prompt Engineering"]
    weak_topics: list[str] = Field(default_factory=list)     # e.g. ["Embeddings", "Async"]
    exercise_hint_avg: float = 0.0  # avg hints used per exercise
    exercise_attempts: int = 0      # total exercise submissions


class ChatRequest(BaseModel):
    lesson_id: str
    message: str
    history: list[ChatMessage] = Field(default_factory=list)
    student_profile: StudentProfile | None = None


class GradeRequest(BaseModel):
    exercise_id: str
    code: str


class TestResultItem(BaseModel):
    name: str
    passed: bool
    message: str = ""


class GradeResponse(BaseModel):
    passed: bool
    score: int = Field(..., ge=0, le=100)
    test_results: list[TestResultItem] = Field(default_factory=list)
    feedback: str = ""


class HintRequest(BaseModel):
    exercise_id: str
    code: str = ""
    hint_level: int = Field(default=1, ge=1, le=3)


class HintResponse(BaseModel):
    hint: str
    level: int


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    model: str
