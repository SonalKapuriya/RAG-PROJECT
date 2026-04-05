# ─────────────────────────────────────────────
# Core feature: Score every resume against a JD
# Returns ranked candidates with scores,
# strengths, gaps and recommendation
# ─────────────────────────────────────────────
import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.schemas.models import LLMSettings, CandidateScore
from app.services.retriever import list_unique_resumes, get_all_chunks_by_resume
from app.services.llm_factory import build_llm


SCORE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert HR screening assistant.
You will be given a Job Description and a candidate's resume content.
Your job is to evaluate how well the candidate matches the job.

Respond ONLY with a valid JSON object in exactly this format:
{{
  "score": <integer 0-100>,
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "gaps": ["gap 1", "gap 2"],
  "summary": "<2 sentence summary of the candidate fit>",
  "recommendation": "<one of: Strong Yes, Yes, Maybe, No>"
}}

Scoring guide:
90-100: Perfect match — meets all requirements, strong bonus skills
70-89:  Good match — meets most requirements
50-69:  Partial match — meets some requirements, notable gaps
30-49:  Weak match — few relevant skills
0-29:   Poor match — does not meet requirements

Do not include any text outside the JSON object."""),
    ("human", """Job Description:
{job_description}

Candidate Resume ({resume_name}):
{resume_content}"""),
])


def _parse_score_response(text: str, resume_name: str) -> CandidateScore | None:
    """Parse LLM JSON response into CandidateScore."""
    try:
        # Strip any markdown fences if present
        clean = re.sub(r"```json|```", "", text).strip()
        data = json.loads(clean)
        return CandidateScore(
            resume_name=resume_name,
            score=int(data.get("score", 0)),
            strengths=data.get("strengths", []),
            gaps=data.get("gaps", []),
            summary=data.get("summary", ""),
            recommendation=data.get("recommendation", "Maybe"),
        )
    except Exception:
        # If parsing fails return a fallback
        return CandidateScore(
            resume_name=resume_name,
            score=0,
            strengths=[],
            gaps=["Could not parse resume evaluation"],
            summary="Evaluation failed for this candidate.",
            recommendation="Maybe",
        )


def score_all_candidates(
    job_description: str,
    top_n: int,
    llm_settings: LLMSettings,
) -> list[CandidateScore]:
    """
    Score every uploaded resume against the job description.
    Returns top_n candidates sorted by score descending.
    """
    resumes = list_unique_resumes()
    if not resumes:
        return []

    llm = build_llm(llm_settings)
    chain = SCORE_PROMPT | llm | StrOutputParser()
    scored: list[CandidateScore] = []

    for resume_info in resumes:
        resume_name = resume_info["filename"]

        # Get all text chunks for this resume
        docs = get_all_chunks_by_resume(resume_name)
        if not docs:
            continue

        # Concatenate all chunks (limit to ~3000 chars to stay within tokens)
        resume_content = "\n".join(d.page_content for d in docs)[:3000]

        # Ask LLM to score
        raw = chain.invoke({
            "job_description": job_description,
            "resume_name": resume_name,
            "resume_content": resume_content,
        })

        candidate = _parse_score_response(raw, resume_name)
        if candidate:
            scored.append(candidate)

    # Sort by score descending and return top_n
    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:top_n]