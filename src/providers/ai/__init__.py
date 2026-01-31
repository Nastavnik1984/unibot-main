"""AI-провайдеры для генерации контента.

Этот пакет реализует плагинную архитектуру для работы с AI-сервисами.
Каждый провайдер — это адаптер, который реализует единый интерфейс BaseProviderAdapter.

Поддерживаемые провайдеры:
- OpenRouter (https://openrouter.ai) — агрегатор моделей
- RouterAI (https://routerai.ru) — российский сервис
- Replicate (https://replicate.com) — платформа ML-моделей (InstantID для открыток)

OpenRouter и RouterAI — OpenAI-совместимые, работают через единый OpenAIAdapter.
Replicate — отдельный адаптер для моделей с сохранением лица.

Пример использования:
    from src.providers.ai import OpenAIAdapter, ReplicateAdapter

    # Для текста/изображений
    adapter = OpenAIAdapter(
        api_key="sk-or-v1-...",
        base_url="https://openrouter.ai/api/v1",
    )
    result = await adapter.generate(
        model_id="openai/gpt-4o",
        prompt="Привет!",
    )

    # Для открыток с сохранением лица
    replicate = ReplicateAdapter(api_key="r8_...")
    result = await replicate.generate(
        model_id="zsxkib/instant-id",
        prompt="New Year card",
        generation_type=GenerationType.POSTCARD,
        image_data=face_photo_bytes,
    )
"""

from src.core.exceptions import GenerationError, ProviderNotAvailableError
from src.providers.ai.base import (
    BaseProviderAdapter,
    GenerationResult,
    GenerationStatus,
    GenerationType,
)
from src.providers.ai.openai_provider import OpenAIAdapter
from src.providers.ai.replicate_provider import ReplicateAdapter

__all__ = [
    "BaseProviderAdapter",
    "GenerationError",
    "GenerationResult",
    "GenerationStatus",
    "GenerationType",
    "OpenAIAdapter",
    "ProviderNotAvailableError",
    "ReplicateAdapter",
]
