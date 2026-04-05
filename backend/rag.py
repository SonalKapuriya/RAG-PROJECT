# ============================================================
# rag.py — All LangChain + Qdrant logic lives here
# main.py will import and use these functions
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue

# ── Config ────────────────────────────────────────────────
GROQ_API_KEY    = os.getenv("GROQ_API_KEY")
QDRANT_URL      = "http://localhost:6333"
COLLECTION_NAME = "hr_resumes"
RESUMES_FOLDER  = "./resumes"
EMBED_MODEL     = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_SIZE     = 384

# ── Singletons (loaded once, reused across requests) ──────
_embeddings   = None
_vectorstore  = None
_rag_chain    = None
_qdrant_client = None


# ============================================================
# EMBEDDINGS — load once, reuse everywhere
# ============================================================

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return _embeddings


# ============================================================
# QDRANT CLIENT — direct client for admin operations
# ============================================================

def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(url=QDRANT_URL)
    return _qdrant_client


# ============================================================
# ENSURE COLLECTION EXISTS
# ============================================================

def ensure_collection():
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
    return True


# ============================================================
# VECTORSTORE — load once, reuse across requests
# ============================================================

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        ensure_collection()
        _vectorstore = QdrantVectorStore.from_existing_collection(
            embedding=get_embeddings(),
            url=QDRANT_URL,
            collection_name=COLLECTION_NAME,
        )
    return _vectorstore


# ============================================================
# INGEST — load PDF → split → embed → store in Qdrant
# Called when HR uploads a new resume
# ============================================================

def ingest_resume(file_path: str, filename: str) -> dict:
    # 1. Load PDF
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # 2. Tag each chunk with the resume filename
    for doc in documents:
        doc.metadata["resume_name"] = filename

    # 3. Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)

    # 4. Store in Qdrant (adds to existing collection)
    ensure_collection()
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME,
    )

    # 5. Reset vectorstore singleton so it picks up new data
    global _vectorstore, _rag_chain
    _vectorstore = None
    _rag_chain   = None

    return {
        "filename": filename,
        "pages": len(documents),
        "chunks": len(chunks)
    }


# ============================================================
# LIST RESUMES — get unique resume names from Qdrant
# ============================================================

def list_resumes() -> list[str]:
    client = get_qdrant_client()
    ensure_collection()

    # Scroll through all points and collect unique resume names
    resume_names = set()
    offset = None

    while True:
        results, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in results:
            name = point.payload.get("metadata", {}).get("resume_name")
            if name:
                resume_names.add(name)

        if next_offset is None:
            break
        offset = next_offset

    return sorted(list(resume_names))


# ============================================================
# DELETE RESUME — remove all vectors for a resume
# ============================================================

def delete_resume(filename: str) -> dict:
    client = get_qdrant_client()

    # Delete all points where resume_name matches
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="metadata.resume_name",
                    match=MatchValue(value=filename)
                )
            ]
        )
    )

    # Also delete the PDF file from disk
    file_path = os.path.join(RESUMES_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Reset singletons
    global _vectorstore, _rag_chain
    _vectorstore = None
    _rag_chain   = None

    return {"deleted": filename}


# ============================================================
# BUILD RAG CHAIN — the core LangChain pipeline
# ============================================================

def get_rag_chain():
    global _rag_chain
    if _rag_chain is not None:
        return _rag_chain

    vectorstore = get_vectorstore()

    # Retriever: find top 5 most relevant chunks
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    # Prompt for single question (no history)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert HR assistant helping screen resumes.
Answer based ONLY on the provided resume context.
Always mention the candidate's name when referring to them.
If the information is not in the context, say 'Not found in the provided resumes'.
Be concise, structured, and helpful."""),
        ("human", """Resume context:
{context}

HR Question: {question}""")
    ])

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=GROQ_API_KEY
    )

    def format_context(docs):
        parts = []
        for doc in docs:
            name = doc.metadata.get("resume_name", "Unknown")
            parts.append(f"--- Resume: {name} ---\n{doc.page_content}")
        return "\n\n".join(parts)

    _rag_chain = (
        {
            "context": retriever | format_context,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return _rag_chain


# ============================================================
# ASK — single question, no memory
# ============================================================

def ask_question(question: str) -> dict:
    chain = get_rag_chain()
    answer = chain.invoke(question)
    return {"question": question, "answer": answer}


# ============================================================
# ASK WITH CHAT HISTORY — remembers previous messages
# chat_history format: [{"role": "human", "content": "..."},
#                        {"role": "ai",    "content": "..."}]
# ============================================================

def ask_with_history(question: str, chat_history: list[dict]) -> dict:
    vectorstore = get_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    # Build history as LangChain message objects
    history_messages = []
    for msg in chat_history:
        if msg["role"] == "human":
            history_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            history_messages.append(AIMessage(content=msg["content"]))

    # Prompt that includes chat history
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert HR assistant helping screen resumes.
Answer based ONLY on the resume context provided.
Always mention the candidate's name when referring to them.
If not found, say 'Not found in the provided resumes'.
Be concise and helpful."""),
        *[(msg.type, msg.content) for msg in history_messages],
        ("human", """Resume context:
{context}

HR Question: {question}""")
    ])
    print("prompt",prompt)

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=GROQ_API_KEY
    )

    def format_context(docs):
        parts = []
        for doc in docs:
            name = doc.metadata.get("resume_name", "Unknown")
            parts.append(f"--- Resume: {name} ---\n{doc.page_content}")
        return "\n\n".join(parts)

    chain = (
        {
            "context": retriever | format_context,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(question)
    return {"question": question, "answer": answer}


# ============================================================
# SHORTLIST — filter candidates by criteria
# ============================================================

def shortlist_candidates(criteria: str) -> dict:
    # Build a specific shortlisting prompt
    vectorstore = get_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}   # get more chunks for shortlisting
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert HR assistant helping shortlist candidates.
Based on the resume context provided, identify and rank candidates who match the criteria.
Format your response as:
1. Candidate name — why they match
2. Candidate name — why they match
...
If no candidates match, say so clearly."""),
        ("human", """Resume context:
{context}

Shortlisting criteria: {question}""")
    ])

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=GROQ_API_KEY
    )

    def format_context(docs):
        parts = []
        for doc in docs:
            name = doc.metadata.get("resume_name", "Unknown")
            parts.append(f"--- Resume: {name} ---\n{doc.page_content}")
        return "\n\n".join(parts)

    chain = (
        {
            "context": retriever | format_context,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    result = chain.invoke(criteria)
    return {"criteria": criteria, "shortlist": result}