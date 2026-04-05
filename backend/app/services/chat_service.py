# ─────────────────────────────────────────────
# RAG chat logic
# Handles both general chat and
# candidate-specific chat
# ─────────────────────────────────────────────
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from app.schemas.models import LLMSettings, ChatMessage
from app.services.retriever import search, search_by_resume
from app.services.llm_factory import build_llm


def _build_history(chat_history: list[ChatMessage]):
    """Convert our schema messages to LangChain messages. Keep last 3 pairs."""
    msgs = chat_history[-6:]
    result = []
    for m in msgs:
        if m.role == "human":
            result.append(HumanMessage(content=m.content))
        else:
            result.append(AIMessage(content=m.content))
    return result


def _format_docs(docs) -> str:
    parts = []
    for doc in docs:
        name = doc.metadata.get("resume_name", "Unknown")
        parts.append(f"--- Resume: {name} ---\n{doc.page_content}")
    return "\n\n".join(parts)


def ask_general(
    question: str,
    chat_history: list[ChatMessage],
    llm_settings: LLMSettings,
) -> str:
    """Ask a question across all resumes."""
    docs = search(question, top_k=llm_settings.top_k)
    context = _format_docs(docs)
    history = _build_history(chat_history)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert HR assistant helping screen candidates.
Answer based ONLY on the resume context provided below.
Always mention candidate names. Be structured and concise.
If the answer is not in the context, say: 'Not found in the uploaded resumes.'

Resume context:
{context}"""),
        *[(m.type, m.content) for m in history],
        ("human", "{question}"),
    ])

    llm = build_llm(llm_settings)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})


def ask_candidate(
    resume_name: str,
    question: str,
    chat_history: list[ChatMessage],
    llm_settings: LLMSettings,
) -> str:
    """Ask a question about one specific candidate."""
    docs = search_by_resume(question, resume_name, top_k=llm_settings.top_k)
    context = _format_docs(docs)
    history = _build_history(chat_history)

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert HR assistant. You are reviewing the resume of: {resume_name}
Answer based ONLY on the resume content below.
Be specific, factual, and concise.
If the answer is not available, say: 'This information is not in the resume.'

Resume content:
{{context}}"""),
        *[(m.type, m.content) for m in history],
        ("human", "{question}"),
    ])

    llm = build_llm(llm_settings)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})