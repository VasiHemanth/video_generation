import asyncio
import threading
import structlog
import time
from typing import Any, List, Optional, Dict, Union, ClassVar
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatResult
from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks import CallbackManagerForLLMRun

logger = structlog.get_logger(__name__)

logger = structlog.get_logger(__name__)

class ChatModelRouter(BaseChatModel):
    """
    A virtual ChatModel that routes requests between multiple providers.
    Supports fallback on RateLimitError (429) and metadata tagging for Langfuse.
    Overrides invoke/ainvoke to stay high-level and avoid breaking internal provider logic.
    """
    primary_model: BaseChatModel
    fallback_models: List[BaseChatModel]
    max_retries_per_model: int = 2
    
    # Global semaphores to enforce limits across all router instances
    _async_semaphores: ClassVar[Dict[str, asyncio.Semaphore]] = {}
    _sync_semaphores: ClassVar[Dict[str, threading.Semaphore]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()
    
    def _get_async_semaphore(self, provider: str) -> asyncio.Semaphore:
        with self._lock:
            if provider not in self._async_semaphores:
                # Cerebras: 3, Groq: 1 (Free tier limits)
                limit = 3 if provider == "cerebras" else 1 if provider == "groq" else 5
                self._async_semaphores[provider] = asyncio.Semaphore(limit)
        return self._async_semaphores[provider]

    def _get_sync_semaphore(self, provider: str) -> threading.Semaphore:
        with self._lock:
            if provider not in self._sync_semaphores:
                limit = 3 if provider == "cerebras" else 1 if provider == "groq" else 5
                self._sync_semaphores[provider] = threading.Semaphore(limit)
        return self._sync_semaphores[provider]
    
    @property
    def _llm_type(self) -> str:
        return "chat-model-router"

    def _generate(self, *args, **kwargs):
        # This is required by BaseChatModel but we prefer using invoke()
        # Fallback to the primary model if called directly via _generate
        return self.primary_model._generate(*args, **kwargs)

    def invoke(
        self,
        input: Union[List[BaseMessage], str],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> BaseMessage:
        all_models = [self.primary_model] + self.fallback_models
        last_exception = None
        
        config = config or {}
        base_metadata = config.get("metadata", {})
        
        for i, model in enumerate(all_models):
            is_fallback = i > 0
            provider_name = self._get_provider_name(model)

            for attempt in range(self.max_retries_per_model + 1):
                try:
                    # Create a new config for the underlying model
                    new_config = config.copy()
                    new_metadata = base_metadata.copy()
                    new_metadata.update({
                        "llm_provider": provider_name,
                        "is_fallback": is_fallback,
                        "fallback_attempt": attempt
                    })
                    new_config["metadata"] = new_metadata
                    
                    if is_fallback:
                        logger.warning(
                            "LLM Fallback active", 
                            provider=provider_name, 
                            attempt=attempt
                        )

                    semaphore = self._get_sync_semaphore(provider_name)
                    with semaphore:
                        return model.invoke(input, config=new_config, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    if self._is_rate_limit(e):
                        logger.warning("Rate limit hit", provider=provider_name)
                        if i < len(all_models) - 1:
                            break # Go to next model
                        else:
                            time.sleep(2 ** (attempt + 1))
                            continue
                    
                    logger.error("LLM Provider Error", provider=provider_name, error=str(e))
                    time.sleep(1 * (attempt + 1))
                    
        if last_exception:
            raise last_exception
        raise Exception("ChatModelRouter failed to any provider.")

    async def ainvoke(
        self,
        input: Union[List[BaseMessage], str],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> BaseMessage:
        all_models = [self.primary_model] + self.fallback_models
        last_exception = None
        
        config = config or {}
        base_metadata = config.get("metadata", {})
        
        for i, model in enumerate(all_models):
            is_fallback = i > 0
            provider_name = self._get_provider_name(model)

            for attempt in range(self.max_retries_per_model + 1):
                try:
                    new_config = config.copy()
                    new_metadata = base_metadata.copy()
                    new_metadata.update({
                        "llm_provider": provider_name,
                        "is_fallback": is_fallback,
                        "fallback_attempt": attempt
                    })
                    new_config["metadata"] = new_metadata
                    
                    semaphore = self._get_async_semaphore(provider_name)
                    async with semaphore:
                        return await model.ainvoke(input, config=new_config, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    if self._is_rate_limit(e):
                        if i < len(all_models) - 1:
                            break
                    
                    import asyncio
                    await asyncio.sleep(1 * (attempt + 1))
                    
        if last_exception:
            raise last_exception
        raise Exception("ChatModelRouter failed to any provider.")

    def _get_provider_name(self, model: BaseChatModel) -> str:
        if hasattr(model, "__class__"):
            class_name = model.__class__.__name__.lower()
            if "groq" in class_name: return "groq"
            if "cerebras" in class_name: return "cerebras"
            if "openai" in class_name: return "openai"
        return "unknown"

    def _is_rate_limit(self, e: Exception) -> bool:
        error_str = str(e).lower()
        return "rate_limit" in error_str or "429" in error_str or "rate limit" in error_str
