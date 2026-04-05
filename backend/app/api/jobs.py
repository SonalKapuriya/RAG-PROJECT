# ─────────────────────────────────────────────
# Job description + scoring routes
# POST /jobs/score — score all resumes vs a JD
# ─────────────────────────────────────────────
from fastapi import APIRouter, HTTPException
from app.schemas.models import ScoreRequest, ScoreResponse
from app.services.scorer import score_all_candidates

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/score", response_model=ScoreResponse)
def score_resumes(request: ScoreRequest):
    """
    The core feature.
    Paste a job description → get every resume scored 0-100
    with strengths, gaps and a hire recommendation.
    Results are sorted best match first.
    """
    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    try:
        candidates = score_all_candidates(
            job_description=request.job_description,
            top_n=request.top_n,
            llm_settings=request.settings,
        )
        return ScoreResponse(
            job_description=request.job_description,
            total_resumes=len(candidates),
            candidates=candidates,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))