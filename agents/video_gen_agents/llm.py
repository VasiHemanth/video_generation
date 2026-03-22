from __future__ import annotations

from langchain_groq import ChatGroq

from .config import Settings


def groq_is_configured(settings: Settings) -> bool:
    return bool(settings.groq_api_key)


def build_groq_chat_model(
    settings: Settings,
    *,
    temperature: float = 0.7,
) -> ChatGroq | None:
    if not settings.groq_api_key:
        return None

    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=temperature,
        max_tokens=4096,
        timeout=30,
    )
