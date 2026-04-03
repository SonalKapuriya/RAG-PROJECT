import os
import logging
from groq import Groq
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from ingestor import get_embedder, get_qdrant, ensure_collection, COLLECTION_NAME
from models import ChatMessage, SourceChunk
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TOP_K = int(os.getenv("TOP_K", 5))

_groq_client: Groq | None = None


def get_groq() -> Groq:
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set. Add it to your .env file.")
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


SYSTEM_PROMPT = """You are an expert HR assistant helping recruiters analyze candidate resumes.

You are given relevant excerpts from candidate resumes retrieved from a vector database.
Your job is to answer the HR's question clearly and helpfully based ONLY on the provided context.

Guidelines:
- Be specific: mention candidate names when relevant
- Be concise but thorough
- If comparing candidates, use a structured format
- If the context doesn't contain enough information to answer, say so honestly
- Never fabricate information not present in the context
- Format your response with clear structure using markdown when listing multiple candidates

Always refer to candidates by name when discussing them.
"""


def retrieve_chunks(query: str, candidate_filter: str | None = None) -> list[dict]:
    """Embed query and retrieve top-k relevant chunks from Qdrant."""
    ensure_collection()
    embedder = get_embedder()
    client = get_qdrant()

    query_vector = embedder.encode(query).tolist()

    search_filter = None
    if candidate_filter:
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="candidate_name",
                    match=MatchValue(value=candidate_filter),
                )
            ]
        )

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=TOP_K,
        query_filter=search_filter,
        with_payload=True,
        score_threshold=0.3,  # ignore very low-similarity results
    )

    return [
        {
            "text": r.payload.get("text", ""),
            "filename": r.payload.get("filename", ""),
            "candidate_name": r.payload.get("candidate_name", "Unknown"),
            "score": round(r.score, 4),
        }
        for r in results
    ]


def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a readable context block."""
    if not chunks:
        return "No relevant resume information found."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"--- Excerpt {i} | Candidate: {chunk['candidate_name']} "
            f"(File: {chunk['filename']}, Relevance: {chunk['score']}) ---\n"
            f"{chunk['text']}"
        )
    return "\n\n".join(parts)


def chat(
    message: str,
    history: list[ChatMessage],
) -> tuple[str, list[SourceChunk]]:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks
    2. Build context
    3. Send to Groq with conversation history
    4. Return answer + source attribution
    """
    chunks = retrieve_chunks(message)

    if not chunks:
        return (
            "I couldn't find any relevant information in the uploaded resumes. "
            "Please make sure resumes have been uploaded and try a different question.",
            [],
        )

    context = build_context(chunks)

    # Build messages for Groq
    groq_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + f"\n\nCONTEXT FROM RESUMES:\n{context}",
        }
    ]

    # Add conversation history (last 6 turns to stay within context window)
    for msg in history[-6:]:
        groq_messages.append({"role": msg.role, "content": msg.content})

    groq_messages.append({"role": "user", "content": message})

    groq = get_groq()
    completion = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=groq_messages,
        temperature=0.2,
        max_tokens=1024,
    )

    answer = completion.choices[0].message.content

    sources = [
        SourceChunk(
            candidate_name=c["candidate_name"],
            filename=c["filename"],
            text=c["text"][:300] + "..." if len(c["text"]) > 300 else c["text"],
            score=c["score"],
        )
        for c in chunks
    ]

    return answer, sources