# ─────────────────────────────────────────────
# Builds the LLM dynamically based on
# provider/model/temperature sent by frontend
# ─────────────────────────────────────────────
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from app.core.config import settings
from app.schemas.models import LLMSettings


# Available models per provider — shown in frontend dropdown
AVAILABLE_MODELS = {
    "groq": [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
    "gemini": [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
    ],
}


def build_llm(llm_settings: LLMSettings) -> BaseChatModel:
    if llm_settings.provider == "groq":
        return ChatGroq(
            model=llm_settings.model,
            temperature=llm_settings.temperature,
            max_tokens=llm_settings.max_tokens,
            api_key=settings.GROQ_API_KEY,
        )
    elif llm_settings.provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=llm_settings.model,
            temperature=llm_settings.temperature,
            max_output_tokens=llm_settings.max_tokens,
            google_api_key=settings.GEMINI_API_KEY,
        )
    else:
        raise ValueError(f"Unknown provider: {llm_settings.provider}")