# ============================================================
# main.py — FastAPI routes
# Run with: uvicorn main:app --reload
# Docs at:  http://localhost:8000/docs
# ============================================================

import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from rag import (
    ingest_resume,
    list_resumes,
    delete_resume,
    ask_question,
    ask_with_history,
    shortlist_candidates,
    get_qdrant_client,
    RESUMES_FOLDER,
    COLLECTION_NAME,
)

# ── App setup ─────────────────────────────────────────────
app = FastAPI(
    title="HR Resume RAG API",
    description="Upload resumes and ask questions about candidates using AI",
    version="1.0.0"
)

# Allow frontend (React/Vue etc.) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Make sure resumes folder exists on startup
os.makedirs(RESUMES_FOLDER, exist_ok=True)


# ============================================================
# REQUEST / RESPONSE MODELS (Pydantic)
# These define what JSON the API accepts and returns
# ============================================================

class QuestionRequest(BaseModel):
    question: str

    class Config:
        json_schema_extra = {
            "example": {"question": "Which candidates know Python?"}
        }


class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[list[dict]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Does he have any leadership experience?",
                "chat_history": [
                    {"role": "human", "content": "Tell me about John"},
                    {"role": "ai",    "content": "John has 5 years of experience..."}
                ]
            }
        }


class ShortlistRequest(BaseModel):
    criteria: str

    class Config:
        json_schema_extra = {
            "example": {"criteria": "Python developer with 3+ years experience and ML knowledge"}
        }


# ============================================================
# HEALTH CHECK
# GET /health
# Check if API and Qdrant are running fine
# ============================================================

@app.get("/health", tags=["System"])
def health_check():
    try:
        client = get_qdrant_client()
        collections = [c.name for c in client.get_collections().collections]
        return {
            "status": "ok",
            "qdrant": "connected",
            "collections": collections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qdrant not reachable: {str(e)}")


# ============================================================
# UPLOAD RESUMES
# POST /resumes/upload
# HR can upload one or multiple PDF files
# Each file is saved to disk + ingested into Qdrant
# ============================================================

@app.post("/resumes/upload", tags=["Resumes"])
async def upload_resumes(files: list[UploadFile] = File(...)):
    """
    Upload one or multiple PDF resumes.
    They will be processed and stored in Qdrant automatically.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    results = []

    for file in files:
        # Validate file type
        if not file.filename.endswith(".pdf"):
            results.append({
                "filename": file.filename,
                "status": "skipped",
                "reason": "Only PDF files are accepted"
            })
            continue

        # Save PDF to disk
        file_path = os.path.join(RESUMES_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Ingest into Qdrant
        try:
            info = ingest_resume(file_path, file.filename)
            results.append({
                "filename": file.filename,
                "status": "success",
                "pages": info["pages"],
                "chunks_stored": info["chunks"]
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "reason": str(e)
            })

    return {"uploaded": results}


# ============================================================
# LIST RESUMES
# GET /resumes/list
# Returns all resumes currently stored in Qdrant
# ============================================================

@app.get("/resumes/list", tags=["Resumes"])
def get_resume_list():
    """
    Get a list of all resumes currently stored in the system.
    """
    try:
        resumes = list_resumes()
        return {
            "total": len(resumes),
            "resumes": resumes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# DELETE RESUME
# DELETE /resumes/{filename}
# Removes a resume from Qdrant AND from disk
# ============================================================

@app.delete("/resumes/{filename}", tags=["Resumes"])
def remove_resume(filename: str):
    """
    Delete a resume by filename.
    This removes all its vectors from Qdrant and deletes the PDF from disk.
    """
    try:
        result = delete_resume(filename)
        return {
            "message": f"Resume '{filename}' deleted successfully",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ASK A QUESTION (no memory)
# POST /ask
# Single question about candidates — no chat history
# Best for: quick lookups
# ============================================================

@app.post("/ask", tags=["Questions"])
def ask(request: QuestionRequest):
    """
    Ask a single question about candidates.
    No memory of previous questions.

    Example questions:
    - Which candidates know Python?
    - Who has a master's degree?
    - List all candidates with startup experience
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = ask_question(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ASK WITH CHAT HISTORY (with memory)
# POST /ask/chat
# Remembers previous messages in the conversation
# Best for: follow-up questions about a candidate
# ============================================================

@app.post("/ask/chat", tags=["Questions"])
def ask_chat(request: ChatRequest):
    """
    Ask a question with conversation memory.
    Pass previous messages in chat_history to maintain context.

    Example: Ask 'Tell me about John' then follow up with
    'Does he have leadership experience?' — it remembers John.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = ask_with_history(request.question, request.chat_history)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# SHORTLIST CANDIDATES
# POST /shortlist
# Give criteria and get ranked list of matching candidates
# Best for: filtering before interviews
# ============================================================

@app.post("/shortlist", tags=["Shortlist"])
def shortlist(request: ShortlistRequest):
    """
    Shortlist candidates based on specific criteria.
    Returns a ranked list of matching candidates with reasons.

    Example criteria:
    - Python developer with 3+ years and ML experience
    - Fresh graduate with good communication skills
    - Senior backend engineer with AWS and Docker
    """
    if not request.criteria.strip():
        raise HTTPException(status_code=400, detail="Criteria cannot be empty")

    try:
        result = shortlist_candidates(request.criteria)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))