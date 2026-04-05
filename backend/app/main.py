# ─────────────────────────────────────────────
# FastAPI app entry point
# All routers registered here
# ─────────────────────────────────────────────
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.qdrant import ensure_collection
from app.api import resumes, chat, jobs

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered resume screening system for HR teams",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    os.makedirs(settings.RESUMES_FOLDER, exist_ok=True)
    ensure_collection()
    print(f"✅ {settings.APP_NAME} started")
    print(f"📦 Qdrant: {settings.QDRANT_URL}")
    print(f"📁 Resumes folder: {settings.RESUMES_FOLDER}")


app.include_router(resumes.router)
app.include_router(chat.router)
app.include_router(jobs.router)


@app.get("/health", tags=["System"])
def health():
    from app.core.qdrant import get_client
    try:
        client = get_client()
        cols = [c.name for c in client.get_collections().collections]
        return {"status": "ok", "qdrant": "connected", "collections": cols}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/", tags=["System"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }