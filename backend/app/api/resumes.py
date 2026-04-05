# ─────────────────────────────────────────────
# Resume routes
# POST /resumes/upload
# GET  /resumes/list
# DELETE /resumes/{filename}
# ─────────────────────────────────────────────
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.schemas.models import UploadResponse, UploadResult, ResumeListResponse, ResumeInfo
from app.services.ingestor import ingest_resume
from app.services.retriever import list_unique_resumes, delete_resume_vectors, reset_vectorstore

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=UploadResponse)
async def upload_resumes(files: list[UploadFile] = File(...)):
    """Upload one or multiple PDF resumes. They are embedded and stored in Qdrant."""
    os.makedirs(settings.RESUMES_FOLDER, exist_ok=True)
    results = []

    for file in files:
        if not file.filename.endswith(".pdf"):
            results.append(UploadResult(
                filename=file.filename, status="skipped",
                reason="Only PDF files accepted"
            ))
            continue

        file_path = os.path.join(settings.RESUMES_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            info = ingest_resume(file_path, file.filename)
            reset_vectorstore()
            results.append(UploadResult(
                filename=file.filename,
                status="success",
                pages=info["pages"],
                chunks=info["chunks"],
            ))
        except Exception as e:
            results.append(UploadResult(
                filename=file.filename,
                status="failed",
                reason=str(e),
            ))

    return UploadResponse(uploaded=results)


@router.get("/list", response_model=ResumeListResponse)
def list_resumes():
    """List all resumes currently indexed in Qdrant."""
    resumes = list_unique_resumes()
    return ResumeListResponse(
        total=len(resumes),
        resumes=[ResumeInfo(**r) for r in resumes],
    )


@router.delete("/{filename}")
def delete_resume(filename: str):
    """Delete a resume — removes vectors from Qdrant and PDF from disk."""
    try:
        delete_resume_vectors(filename)
        file_path = os.path.join(settings.RESUMES_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"message": f"'{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))