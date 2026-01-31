"""Адаптер для Replicate API.

Этот модуль реализует интеграцию с Replicate для:
- Генерации открыток с сохранением лица (InstantID)
- Других image-to-image моделей с face preservation

Replicate — платформа для запуска ML-моделей в облаке.
Особенность: модели запускаются асинхронно, нужно ждать результат.

Документация: https://replicate.com/docs
"""

from __future__ import annotations

import asyncio
import base64
from typing import TYPE_CHECKING, Any

import httpx
from typing_extensions import override

from src.core.exceptions import GenerationError
from src.providers.ai.base import (
    BaseProviderAdapter,
    GenerationResult,
    GenerationStatus,
    GenerationType,
)
from src.providers.ai.registry import register_provider
from src.utils.logging import get_logger

if TYPE_CHECKING:
    from src.config.models import AIProvidersSettings

logger = get_logger(__name__)

# Типы генерации, которые поддерживает Replicate
SUPPORTED_GENERATION_TYPES = frozenset(
    {
        GenerationType.POSTCARD,  # Открытки с сохранением лица
        GenerationType.IMAGE,  # Обычные изображения
    }
)

# Таймаут для HTTP-запросов (в секундах)
DEFAULT_TIMEOUT_SECONDS = 180.0

# Интервал опроса статуса prediction (в секундах)
POLL_INTERVAL_SECONDS = 2.0

# Максимальное количество попыток опроса (180 сек / 2 сек = 90 попыток)
MAX_POLL_ATTEMPTS = 90

# URL API Replicate
REPLICATE_API_URL = "https://api.replicate.com/v1"


class ReplicateAdapter(BaseProviderAdapter):
    """Адаптер для Replicate API.

    Поддерживает:
    - InstantID для генерации открыток с сохранением черт лица
    - Другие image-to-image модели

    Пример использования:
        adapter = ReplicateAdapter(api_key="r8_...")

        # Генерация открытки с лицом пользователя
        result = await adapter.generate(
            model_id="zsxkib/instant-id",
            prompt="New Year greeting card with Santa hat",
            generation_type=GenerationType.POSTCARD,
            image_data=face_photo_bytes,  # Фото лица
        )
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        proxy_url: str | None = None,
    ) -> None:
        """Создать адаптер Replicate API.

        Args:
            api_key: API-ключ Replicate (формат: r8_...).
                Получить: https://replicate.com/account/api-tokens
            timeout: Таймаут HTTP-запросов в секундах.
            proxy_url: URL прокси-сервера (опционально).
        """
        self._api_key = api_key
        self._timeout = timeout
        self._proxy_url = proxy_url

        # HTTP клиент для запросов
        self._client = httpx.AsyncClient(
            base_url=REPLICATE_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
            proxy=proxy_url,
        )

    @property
    @override
    def provider_name(self) -> str:
        """Название провайдера."""
        return "replicate"

    @override
    def supports_capability(self, generation_type: GenerationType) -> bool:
        """Проверить поддержку типа генерации."""
        return generation_type in SUPPORTED_GENERATION_TYPES

    @override
    async def generate(
        self,
        model_id: str,
        prompt: str,
        *,
        generation_type: GenerationType,
        **kwargs: Any,
    ) -> GenerationResult:
        """Выполнить генерацию через Replicate API.

        Args:
            model_id: ID модели (например: zsxkib/instant-id).
            prompt: Текстовое описание желаемого результата.
            generation_type: Тип генерации.
            **kwargs:
                - image_data: bytes — фото лица для POSTCARD.
                - negative_prompt: str — что НЕ генерировать.
                - ip_adapter_scale: float — сила сохранения лица (0.0-1.0).

        Returns:
            GenerationResult с URL сгенерированного изображения.

        Raises:
            GenerationError: При ошибке API.
        """
        if not self.supports_capability(generation_type):
            raise GenerationError(
                f"Replicate не поддерживает {generation_type.value}",
                provider=self.provider_name,
                model_id=model_id,
                is_retryable=False,
            )

        try:
            if generation_type == GenerationType.POSTCARD:
                return await self._generate_postcard(model_id, prompt, **kwargs)
            elif generation_type == GenerationType.IMAGE:
                return await self._generate_image(model_id, prompt, **kwargs)
            else:
                raise GenerationError(
                    f"Неизвестный тип генерации: {generation_type}",
                    provider=self.provider_name,
                    model_id=model_id,
                    is_retryable=False,
                )
        except GenerationError:
            raise
        except Exception as e:
            logger.exception(
                "Ошибка Replicate API (model=%s, generation_type=%s)",
                model_id,
                generation_type,
            )
            raise GenerationError(
                str(e),
                provider=self.provider_name,
                model_id=model_id,
                is_retryable=self._is_retryable_error(e),
                original_error=e,
            ) from e

    async def _generate_postcard(
        self,
        model_id: str,
        prompt: str,
        **kwargs: Any,
    ) -> GenerationResult:
        """Генерация открытки с сохранением черт лица через PhotoMaker.

        PhotoMaker — модель, которая генерирует изображения с лицом человека
        из reference-фото. Отлично подходит для открыток!

        Args:
            model_id: ID модели PhotoMaker.
            prompt: Описание открытки (стиль, праздник, элементы).
            **kwargs:
                - image_data: bytes — фото лица пользователя (ОБЯЗАТЕЛЬНО).
                - style_name: str — стиль изображения.
                - num_steps: int — количество шагов (качество).
                - style_strength_ratio: int — сила стилизации.
                - num_outputs: int — количество выходных изображений.
                - guidance_scale: float — насколько точно следовать промпту.

        Returns:
            GenerationResult с URL открытки.
        """
        image_data = kwargs.get("image_data")
        if not image_data:
            raise GenerationError(
                "Для генерации открытки необходимо передать image_data (фото лица)",
                provider=self.provider_name,
                model_id=model_id,
                is_retryable=False,
            )

        # Кодируем изображение в base64 data URL
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        # Параметры для PhotoMaker
        style_name = kwargs.get("style_name", "Photographic (Default)")
        num_steps = kwargs.get("num_steps", 50)
        style_strength_ratio = kwargs.get("style_strength_ratio", 20)
        num_outputs = kwargs.get("num_outputs", 1)
        guidance_scale = kwargs.get("guidance_scale", 5)

        # Что НЕ генерировать
        negative_prompt = kwargs.get(
            "negative_prompt",
            "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, "
            "extra digit, fewer digits, cropped, worst quality, low quality, "
            "normal quality, jpeg artifacts, signature, watermark, username, blurry",
        )

        logger.debug(
            "Replicate PhotoMaker: model=%s, image_size=%d bytes, prompt='%s'",
            model_id,
            len(image_data),
            prompt[:100],
        )

        # PhotoMaker требует специальный формат промпта с "img" плейсхолдером
        # Это указывает модели где использовать лицо с фото
        photomaker_prompt = f"img, {prompt}"

        # Формируем входные данные для модели PhotoMaker
        input_data = {
            "input_image": image_data_url,
            "prompt": photomaker_prompt,
            "negative_prompt": negative_prompt,
            "style_name": style_name,
            "num_steps": num_steps,
            "style_strength_ratio": style_strength_ratio,
            "num_outputs": num_outputs,
            "guidance_scale": guidance_scale,
        }

        # Создаём prediction
        prediction_id = await self._create_prediction(model_id, input_data)

        # Ждём завершения
        result = await self._wait_for_prediction(prediction_id, model_id)

        return result

    async def _generate_image(
        self,
        model_id: str,
        prompt: str,
        **kwargs: Any,
    ) -> GenerationResult:
        """Генерация изображения (без сохранения лица).

        Args:
            model_id: ID модели.
            prompt: Описание изображения.
            **kwargs: Параметры модели.

        Returns:
            GenerationResult с URL изображения.
        """
        negative_prompt = kwargs.get("negative_prompt", "")
        num_steps = kwargs.get("num_inference_steps", 30)

        input_data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "num_inference_steps": num_steps,
        }

        logger.debug(
            "Replicate Image: model=%s, prompt='%s'",
            model_id,
            prompt[:100],
        )

        prediction_id = await self._create_prediction(model_id, input_data)
        result = await self._wait_for_prediction(prediction_id, model_id)

        return result

    async def _create_prediction(
        self,
        model_id: str,
        input_data: dict[str, Any],
    ) -> str:
        """Создать prediction (запустить генерацию).

        Args:
            model_id: ID модели (owner/model или owner/model:version).
            input_data: Входные данные для модели.

        Returns:
            ID созданного prediction.
        """
        # Replicate API поддерживает два способа запуска:
        # 1. POST /predictions с {"version": "abc123..."} — нужен хэш версии
        # 2. POST /models/{owner}/{name}/predictions — автовыбор последней версии
        #
        # Используем способ 2, т.к. он не требует знать хэш версии

        if ":" in model_id:
            # Явно указана версия — используем стандартный эндпоинт
            version = model_id.split(":")[-1]
            payload = {"version": version, "input": input_data}
            endpoint = "/predictions"
        else:
            # Версия не указана — используем эндпоинт модели (автовыбор версии)
            # Формат model_id: owner/model -> эндпоинт: /models/owner/model/predictions
            payload = {"input": input_data}
            endpoint = f"/models/{model_id}/predictions"

        response = await self._client.post(endpoint, json=payload)

        if response.status_code != 201:
            error_text = response.text
            logger.error(
                "Ошибка создания prediction: status=%d, response=%s",
                response.status_code,
                error_text[:500],
            )
            raise GenerationError(
                f"Replicate API вернул ошибку: {error_text[:200]}",
                provider=self.provider_name,
                model_id=model_id,
                is_retryable=response.status_code >= 500,
            )

        data = response.json()
        prediction_id = data.get("id")

        if not prediction_id:
            raise GenerationError(
                "Replicate не вернул prediction ID",
                provider=self.provider_name,
                model_id=model_id,
                is_retryable=True,
            )

        logger.debug("Создан prediction: id=%s", prediction_id)
        return prediction_id

    async def _wait_for_prediction(
        self,
        prediction_id: str,
        model_id: str,
    ) -> GenerationResult:
        """Ждать завершения prediction (опрашивать статус).

        Args:
            prediction_id: ID prediction.
            model_id: ID модели (для логирования).

        Returns:
            GenerationResult с результатом.
        """
        for attempt in range(MAX_POLL_ATTEMPTS):
            response = await self._client.get(f"/predictions/{prediction_id}")

            if response.status_code != 200:
                raise GenerationError(
                    f"Ошибка получения статуса: {response.text[:200]}",
                    provider=self.provider_name,
                    model_id=model_id,
                    is_retryable=True,
                )

            data = response.json()
            status = data.get("status")

            logger.debug(
                "Prediction status: id=%s, status=%s, attempt=%d/%d",
                prediction_id,
                status,
                attempt + 1,
                MAX_POLL_ATTEMPTS,
            )

            if status == "succeeded":
                # Генерация успешно завершена
                output = data.get("output")
                # output может быть строкой (URL) или списком URL
                if isinstance(output, list) and len(output) > 0:
                    image_url = output[0]
                elif isinstance(output, str):
                    image_url = output
                else:
                    raise GenerationError(
                        "Replicate вернул пустой output",
                        provider=self.provider_name,
                        model_id=model_id,
                        is_retryable=True,
                    )

                logger.info(
                    "Prediction завершён: id=%s, url=%s",
                    prediction_id,
                    image_url[:80],
                )

                return GenerationResult(
                    status=GenerationStatus.SUCCESS,
                    content=image_url,
                    prediction_id=prediction_id,
                    raw_response=data,
                )

            elif status == "failed":
                # Генерация не удалась
                error = data.get("error", "Unknown error")
                logger.error("Prediction failed: id=%s, error=%s", prediction_id, error)
                raise GenerationError(
                    f"Генерация не удалась: {error}",
                    provider=self.provider_name,
                    model_id=model_id,
                    is_retryable=False,
                )

            elif status == "canceled":
                raise GenerationError(
                    "Генерация была отменена",
                    provider=self.provider_name,
                    model_id=model_id,
                    is_retryable=False,
                )

            elif status in ("starting", "processing"):
                # Ещё выполняется — ждём
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
            else:
                # Неизвестный статус — ждём
                logger.warning("Неизвестный статус prediction: %s", status)
                await asyncio.sleep(POLL_INTERVAL_SECONDS)

        # Превышено максимальное время ожидания
        raise GenerationError(
            f"Превышено время ожидания ({MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS}с)",
            provider=self.provider_name,
            model_id=model_id,
            is_retryable=True,
        )

    @override
    async def get_prediction_status(self, prediction_id: str) -> GenerationResult:
        """Получить статус prediction.

        Args:
            prediction_id: ID prediction.

        Returns:
            GenerationResult с текущим статусом.
        """
        response = await self._client.get(f"/predictions/{prediction_id}")

        if response.status_code != 200:
            raise GenerationError(
                f"Ошибка получения статуса: {response.text[:200]}",
                provider=self.provider_name,
                model_id="unknown",
                is_retryable=True,
            )

        data = response.json()
        status = data.get("status")

        if status == "succeeded":
            output = data.get("output")
            image_url = output[0] if isinstance(output, list) else output
            return GenerationResult(
                status=GenerationStatus.SUCCESS,
                content=image_url,
                prediction_id=prediction_id,
            )
        elif status == "failed":
            return GenerationResult(
                status=GenerationStatus.FAILED,
                error_message=data.get("error"),
                prediction_id=prediction_id,
            )
        elif status == "canceled":
            return GenerationResult(
                status=GenerationStatus.CANCELED,
                prediction_id=prediction_id,
            )
        else:
            return GenerationResult(
                status=GenerationStatus.PROCESSING,
                prediction_id=prediction_id,
            )

    @override
    async def cancel_prediction(self, prediction_id: str) -> bool:
        """Отменить prediction.

        Args:
            prediction_id: ID prediction.

        Returns:
            True если отмена успешна.
        """
        try:
            response = await self._client.post(f"/predictions/{prediction_id}/cancel")
            return response.status_code == 200
        except Exception:
            logger.exception("Ошибка отмены prediction: %s", prediction_id)
            return False

    def _is_retryable_error(self, error: Exception) -> bool:
        """Определить, можно ли повторить запрос."""
        error_message = str(error).lower()
        retryable_patterns = [
            "rate limit",
            "timeout",
            "connection",
            "server error",
            "502",
            "503",
            "504",
        ]
        return any(pattern in error_message for pattern in retryable_patterns)

    async def close(self) -> None:
        """Закрыть HTTP-клиент."""
        await self._client.aclose()


# ==============================================================================
# ФАБРИКА АДАПТЕРОВ
# ==============================================================================


class ReplicateAdapterFactory:
    """Фабрика для создания Replicate-адаптеров."""

    def create(
        self,
        settings: AIProvidersSettings,
        proxy_url: str | None = None,
        timeout: float | None = None,
    ) -> BaseProviderAdapter | None:
        """Создать адаптер если настроен API-ключ."""
        api_key = getattr(settings, "replicate_api_key", None)
        if api_key is None:
            return None

        return ReplicateAdapter(
            api_key=api_key.get_secret_value(),
            proxy_url=proxy_url,
            timeout=timeout or DEFAULT_TIMEOUT_SECONDS,
        )


# ==============================================================================
# РЕГИСТРАЦИЯ ПРОВАЙДЕРА
# ==============================================================================

# Регистрируем Replicate — платформа для запуска ML-моделей
# URL: https://replicate.com
# API-ключ: AI__REPLICATE_API_KEY
register_provider("replicate", ReplicateAdapterFactory())

