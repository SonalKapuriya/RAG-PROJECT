from pydantic import BaseModel
from typing import Optional


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class SourceChunk(BaseModel):
    candidate_name: str
    filename: str
    text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


class IngestResponse(BaseModel):
    message: str
    files_processed: int
    chunks_stored: int
    errors: list[str] = []


class Candidate(BaseModel):
    name: str
    filename: str
    chunk_count: int


class CandidatesResponse(BaseModel):
    candidates: list[Candidate]
    total: int