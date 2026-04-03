import os
import re
import uuid
import logging
from pathlib import Path

import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "resumes")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "llama-3.3-70b-versatile")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))

# Lazy-loaded singletons
_embedder: SentenceTransformer | None = None
_qdrant: QdrantClient | None = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def get_qdrant() -> QdrantClient:
    global _qdrant
    if _qdrant is None:
        _qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _qdrant


def ensure_collection():
    """Create Qdrant collection if it doesn't exist."""
    client = get_qdrant()
    embedder = get_embedder()
    dim = embedder.get_sentence_embedding_dimension()

    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        logger.info(f"Created Qdrant collection '{COLLECTION_NAME}' (dim={dim})")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using PyMuPDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    doc.close()
    return "\n".join(pages)


def infer_candidate_name(text: str, filename: str) -> str:
    """
    Best-effort candidate name extraction.
    Strategy: take the first non-empty line of the resume (usually the name),
    then fall back to the filename stem.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:5]:
        # A name is typically 2-4 words, no digits or special chars
        if re.match(r"^[A-Za-z]+(?: [A-Za-z]+){1,3}$", line):
            return line
    # Fallback: filename without extension and underscores/dashes replaced
    stem = Path(filename).stem
    return re.sub(r"[_\-]+", " ", stem).title()


def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)


def delete_candidate(filename: str):
    """Remove all chunks for a previously uploaded resume."""
    client = get_qdrant()
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[FieldCondition(key="filename", match=MatchValue(value=filename))]
        ),
    )


def ingest_pdf(pdf_bytes: bytes, filename: str) -> int:
    """
    Parse → chunk → embed → upsert into Qdrant.
    Returns number of chunks stored.
    """
    ensure_collection()
    client = get_qdrant()
    embedder = get_embedder()

    # Remove stale data for re-uploads of same file
    delete_candidate(filename)

    raw_text = extract_text_from_pdf(pdf_bytes)
    if not raw_text.strip():
        raise ValueError(f"Could not extract text from {filename}")

    candidate_name = infer_candidate_name(raw_text, filename)
    chunks = chunk_text(raw_text)

    if not chunks:
        raise ValueError(f"No chunks produced from {filename}")

    logger.info(f"Ingesting '{candidate_name}' ({filename}) — {len(chunks)} chunks")

    vectors = embedder.encode(chunks, show_progress_bar=False).tolist()

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={
                "text": chunk,
                "filename": filename,
                "candidate_name": candidate_name,
                "chunk_index": i,
            },
        )
        for i, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(chunks)


def list_candidates() -> list[dict]:
    """Return unique candidates stored in Qdrant."""
    client = get_qdrant()
    print("client:",client)
    ensure_collection()

    # Scroll through all points and aggregate by filename
    seen: dict[str, dict] = {}
    offset = None

    while True:
        results, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in results:
            fn = point.payload.get("filename", "unknown")
            if fn not in seen:
                seen[fn] = {
                    "filename": fn,
                    "name": point.payload.get("candidate_name", "Unknown"),
                    "chunk_count": 0,
                }
            seen[fn]["chunk_count"] += 1

        if offset is None:
            break

    return list(seen.values())