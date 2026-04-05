# ─────────────────────────────────────────────
# Vector search — fetch relevant chunks
# from Qdrant for a given query
# ─────────────────────────────────────────────
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.core.config import settings
from app.services.ingestor import get_embeddings

_vectorstore: QdrantVectorStore | None = None


def get_vectorstore() -> QdrantVectorStore:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = QdrantVectorStore.from_existing_collection(
            embedding=get_embeddings(),
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name=settings.COLLECTION_NAME,
        )
    return _vectorstore


def reset_vectorstore():
    """Call this after uploading or deleting resumes."""
    global _vectorstore
    _vectorstore = None


def search(query: str, top_k: int = 5) -> list[Document]:
    """Search across all resumes."""
    vs = get_vectorstore()
    return vs.similarity_search(query, k=top_k)


def search_by_resume(
    query: str,
    resume_name: str,
    top_k: int = 5
) -> list[Document]:
    """Search within a single resume only."""
    vs = get_vectorstore()
    return vs.similarity_search(
        query,
        k=top_k,
        filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.resume_name",
                    match=MatchValue(value=resume_name),
                )
            ]
        ),
    )


def get_all_chunks_by_resume(resume_name: str) -> list[Document]:
    """Get all chunks for a specific resume — used for scoring."""
    from app.core.qdrant import get_client
    client = get_client()
    results, _ = client.scroll(
        collection_name=settings.COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.resume_name",
                    match=MatchValue(value=resume_name),
                )
            ]
        ),
        limit=100,
        with_payload=True,
        with_vectors=False,
    )
    docs = []
    for point in results:
        content = point.payload.get("page_content", "")
        metadata = point.payload.get("metadata", {})
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def list_unique_resumes() -> list[dict]:
    """Return all unique resume names + chunk counts."""
    from app.core.qdrant import get_client
    client = get_client()

    counts: dict[str, int] = {}
    offset = None

    while True:
        results, next_offset = client.scroll(
            collection_name=settings.COLLECTION_NAME,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in results:
            name = point.payload.get("metadata", {}).get("resume_name")
            if name:
                counts[name] = counts.get(name, 0) + 1
        if next_offset is None:
            break
        offset = next_offset

    return [{"filename": k, "chunks": v} for k, v in sorted(counts.items())]


def delete_resume_vectors(filename: str):
    """Delete all vectors for a resume."""
    from app.core.qdrant import get_client
    from qdrant_client.models import FilterSelector
    client = get_client()
    client.delete(
        collection_name=settings.COLLECTION_NAME,
        points_selector=FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.resume_name",
                        match=MatchValue(value=filename),
                    )
                ]
            )
        ),
    )
    reset_vectorstore()