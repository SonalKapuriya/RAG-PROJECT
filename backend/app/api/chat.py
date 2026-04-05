# ─────────────────────────────────────────────
# Chat routes
# POST /chat/ask          — general across all resumes
# POST /chat/ask-candidate — ask about one candidate
# GET  /chat/models        — available models per provider
# ─────────────────────────────────────────────
from fastapi import APIRouter, HTTPException
from app.schemas.models import AskRequest, CandidateAskRequest
from app.services.chat_service import ask_general, ask_candidate
from app.services.llm_factory import AVAILABLE_MODELS

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/ask")
def ask(request: AskRequest):
    """Ask a question across all uploaded resumes."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        answer = ask_general(
            question=request.question,
            chat_history=request.chat_history,
            llm_settings=request.settings,
        )
        return {"question": request.question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask-candidate")
def ask_about_candidate(request: CandidateAskRequest):
    """Ask a question about one specific candidate."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        answer = ask_candidate(
            resume_name=request.resume_name,
            question=request.question,
            chat_history=request.chat_history,
            llm_settings=request.settings,
        )
        return {
            "resume_name": request.resume_name,
            "question": request.question,
            "answer": answer,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
def get_models():
    """Returns available models per provider for the frontend dropdown."""
    return AVAILABLE_MODELS