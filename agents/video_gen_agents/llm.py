from __future__ import annotations

import structlog
from langchain_groq import ChatGroq
from langchain_cerebras import ChatCerebras
from .router import ChatModelRouter

from typing import Any
from .config import Settings

logger = structlog.get_logger(__name__)

# Galileo State
_GALILEO_INITIALIZED = False

# Langfuse State
_LANGFUSE_INITIALIZED = False


def initialize_galileo(settings: Settings) -> bool:
    """Checks if Galileo is configured and available in the environment."""
    global _GALILEO_INITIALIZED

    if _GALILEO_INITIALIZED:
        return True

    if not settings.galileo_api_key:
        logger.info("ℹ Galileo not configured - continuing without evaluation metrics")
        return False

    try:
        from galileo import galileo_context
        _GALILEO_INITIALIZED = True
        logger.info("✓ Galileo evaluation metrics available (Session-based)")
        return True
    except ImportError:
        logger.warning("ℹ Galileo not available - continuing without evaluation metrics")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to initialize Galileo: {e}")
        return False


def start_galileo_session(project_id: str, session_name: str) -> list[Any] | None:
    """Starts a Galileo session and returns the contextual callback handler."""
    if not _GALILEO_INITIALIZED:
        return None

    try:
        from galileo import galileo_context
        from galileo.handlers.langchain import GalileoAsyncCallback
        galileo_context.start_session(name=session_name, external_id=project_id)
        galileo_callback = GalileoAsyncCallback()
        return [galileo_callback]
    except Exception as e:
        logger.warning(f"Failed to start Galileo session: {e}")
        return None


def initialize_langfuse(settings: Settings) -> bool:
    """Checks if Langfuse is configured and available."""
    global _LANGFUSE_INITIALIZED

    if _LANGFUSE_INITIALIZED:
        return True

    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        logger.info("ℹ Langfuse not configured - continuing without Langfuse tracing")
        return False

    try:
        import langfuse
        _LANGFUSE_INITIALIZED = True
        logger.info("✓ Langfuse observability metrics available")
        return True
    except ImportError:
        logger.warning("ℹ Langfuse library not available - continuing without Langfuse tracing")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to initialize Langfuse: {e}")
        return False


def get_langfuse_callback(project_id: str, session_name: str) -> list[Any] | None:
    """Returns the Langfuse Callback handler scoped to the project trace."""
    if not _LANGFUSE_INITIALIZED:
        return None

    try:
        from langfuse.langchain import CallbackHandler
        langfuse_handler = CallbackHandler()
        return [langfuse_handler]
    except Exception as e:
        logger.warning(f"Failed to initialize Langfuse callback: {e}")
        return None


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


def build_cerebras_chat_model(
    settings: Settings,
    *,
    temperature: float = 0.7,
) -> ChatCerebras | None:
    if not settings.cerebras_api_key:
        return None

    return ChatCerebras(
        api_key=settings.cerebras_api_key,
        model=settings.cerebras_model,
        temperature=temperature,
    )


def build_resilient_model(
    settings: Settings,
    *,
    temperature: float = 0.7,
) -> ChatModelRouter | ChatGroq | ChatCerebras | None:
    """
    Builds a resilient model that prefers Cerebras but falls back to Groq on 429 errors.
    """
    primary = build_cerebras_chat_model(settings, temperature=temperature)
    secondary = build_groq_chat_model(settings, temperature=temperature)
    
    if primary and secondary:
        return ChatModelRouter(
            primary_model=primary,
            fallback_models=[secondary]
        )
    
    return primary or secondary
