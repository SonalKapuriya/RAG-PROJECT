# ─────────────────────────────────────────────
# All Pydantic request and response models
# ─────────────────────────────────────────────
from pydantic import BaseModel, Field
from typing import Literal, Optional


# ── LLM Settings (sent by frontend dynamically) ──
class LLMSettings(BaseModel):
    provider: Literal["groq", "gemini"] = "groq"
    model: str = "llama-3.1-8b-instant"
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, ge=128, le=4096)
    top_k: int = Field(default=5, ge=1, le=20)


# ── Chat message ──
class ChatMessage(BaseModel):
    role: Literal["human", "ai"]
    content: str


# ── /chat/ask request ──
class AskRequest(BaseModel):
    question: str
    chat_history: list[ChatMessage] = []
    settings: LLMSettings = LLMSettings()

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Which candidates know Python?",
                "chat_history": [],
                "settings": {
                    "provider": "groq",
                    "model": "llama-3.1-8b-instant",
                    "temperature": 0.0,
                    "max_tokens": 1024,
                    "top_k": 5
                }
            }
        }


# ── /jobs/score request ──
class ScoreRequest(BaseModel):
    job_description: str
    top_n: int = Field(default=10, ge=1, le=50)
    settings: LLMSettings = LLMSettings()

    class Config:
        json_schema_extra = {
            "example": {
                "job_description": "Looking for a Python developer with 3+ years experience in ML and FastAPI.",
                "top_n": 10,
                "settings": {
                    "provider": "groq",
                    "model": "llama-3.1-8b-instant",
                    "temperature": 0.0,
                    "max_tokens": 1024,
                    "top_k": 5
                }
            }
        }


# ── /jobs/score response ──
class CandidateScore(BaseModel):
    resume_name: str
    score: int                  # 0-100
    strengths: list[str]
    gaps: list[str]
    summary: str
    recommendation: Literal["Strong Yes", "Yes", "Maybe", "No"]


class ScoreResponse(BaseModel):
    job_description: str
    total_resumes: int
    candidates: list[CandidateScore]


# ── /chat/ask-candidate request ──
class CandidateAskRequest(BaseModel):
    resume_name: str            # filter to only this candidate
    question: str
    chat_history: list[ChatMessage] = []
    settings: LLMSettings = LLMSettings()


# ── Resume info ──
class ResumeInfo(BaseModel):
    filename: str
    chunks: int


class ResumeListResponse(BaseModel):
    total: int
    resumes: list[ResumeInfo]


# ── Upload response ──
class UploadResult(BaseModel):
    filename: str
    status: Literal["success", "failed", "skipped"]
    pages: int = 0
    chunks: int = 0
    reason: str = ""


class UploadResponse(BaseModel):
    uploaded: list[UploadResult]