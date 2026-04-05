# ─────────────────────────────────────────────
# PDF loading, chunking, embedding, storing
# Called when HR uploads a resume
# ─────────────────────────────────────────────
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from app.core.config import settings
from app.core.qdrant import ensure_collection

_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBED_MODEL
        )
    return _embeddings


def ingest_resume(file_path: str, filename: str) -> dict:
    # 1. Load PDF pages
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # 2. Tag every chunk with resume filename
    for doc in documents:
        doc.metadata["resume_name"] = filename

    # 3. Split into overlapping chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(documents)

    # 4. Embed and store in Qdrant
    ensure_collection()
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        collection_name=settings.COLLECTION_NAME,
    )

    return {
        "filename": filename,
        "pages": len(documents),
        "chunks": len(chunks),
    }