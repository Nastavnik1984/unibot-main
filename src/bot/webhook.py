"""Утилиты для работы с Telegram webhook.

Этот модуль содержит логику:
- Нормализации домена из APP__DOMAIN
- Формирования webhook URL
- Установки webhook с retry-логикой
- Удаления webhook при переходе в polling mode
"""

import asyncio
from urllib.parse import urljoin, urlparse

from aiogram import Bot

from src.utils.logging import get_logger

logger = get_logger(__name__)

# Константы для webhook
WEBHOOK_PATH = "/api/telegram/webhook"
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s


def normalize_domain(domain: str) -> str:
    """Нормализовать домен для webhook URL.

    Логика нормализации (из PRD):
    1. Добавляет https:// если не указан протокол
    2. Удаляет лишние слеши в конце
    3. Извлекает чистый домен

    Args:
        domain: Домен из APP__DOMAIN (example.com или https://example.com/).

    Returns:
        Нормализованный домен с протоколом (https://example.com).

    Example:
        >>> normalize_domain("example.com")
        "https://example.com"
        >>> normalize_domain("https://example.com/")
        "https://example.com"
        >>> normalize_domain("http://example.com")
        "http://example.com"
    """
    domain = domain.strip()

    # Добавляем https:// если протокол не указан
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"

    # Парсим URL для нормализации
    parsed = urlparse(domain)

    # Формируем нормализованный домен: scheme://netloc
    # Удаляем path, query, fragment если они были указаны
    return f"{parsed.scheme}://{parsed.netloc}"


def build_webhook_url(domain: str) -> str:
    """Построить полный webhook URL.

    Args:
        domain: Нормализованный домен (https://example.com).

    Returns:
        Полный webhook URL (https://example.com/api/telegram/webhook).

    Example:
        >>> build_webhook_url("https://example.com")
        "https://example.com/api/telegram/webhook"
    """
    # urljoin корректно обрабатывает случаи с/без слеша в конце
    return urljoin(domain, WEBHOOK_PATH)


async def setup_webhook(bot: Bot, domain: str) -> bool:
    """Установить webhook с retry-логикой.

    Согласно PRD (раздел 2.3):
    - До 3 попыток с exponential backoff (1s, 2s, 4s)
    - При временных ошибках (5xx, timeout, сетевые) — повторяем
    - При ошибках валидации (4xx, некорректный URL) — фатально

    Args:
        bot: Инстанс Telegram бота.
        domain: Нормализованный домен (https://example.com).

    Returns:
        True если webhook установлен успешно, False при критической ошибке.

    Raises:
        RuntimeError: При критических ошибках валидации (4xx).
    """
    webhook_url = build_webhook_url(domain)

    logger.info("Установка webhook: %s", webhook_url)

    for attempt in range(MAX_RETRIES):
        try:
            # Устанавливаем webhook
            result = await bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=False,  # Не удаляем непрочитанные update
            )

            if result:
                logger.info("✓ Webhook успешно установлен: %s", webhook_url)
                return True

            # Telegram вернул False — что-то не так
            logger.warning(
                "Telegram вернул False при установке webhook (попытка %d/%d)",
                attempt + 1,
                MAX_RETRIES,
            )

        except Exception as e:
            error_message = str(e)

            # Проверяем тип ошибки по сообщению
            client_error_keywords = [
                "400",
                "401",
                "403",
                "404",
                "invalid url",
                "bad request",
            ]
            is_client_error = any(
                keyword in error_message.lower() for keyword in client_error_keywords
            )

            if is_client_error:
                # 4xx ошибка — проблема с URL или конфигурацией
                logger.error(
                    "✗ Критическая ошибка валидации webhook: %s", error_message
                )
                raise RuntimeError(
                    f"Некорректный webhook URL или конфигурация: {error_message}"
                ) from e

            # Временная ошибка (5xx, сеть, таймаут)
            logger.warning(
                "Временная ошибка установки webhook (попытка %d/%d): %s",
                attempt + 1,
                MAX_RETRIES,
                error_message,
            )

        # Если не последняя попытка — ждём перед retry
        if attempt < MAX_RETRIES - 1:
            delay = RETRY_DELAYS[attempt]
            logger.info("Повтор через %d секунд...", delay)
            await asyncio.sleep(delay)

    # Все попытки исчерпаны
    logger.error(
        "✗ Не удалось установить webhook после %d попыток. "
        "Приложение не может работать в PROD без webhook.",
        MAX_RETRIES,
    )
    return False


async def remove_webhook(bot: Bot) -> None:
    """Удалить webhook (переход в polling mode).

    Args:
        bot: Инстанс Telegram бота.
    """
    logger.info("Удаление webhook (переход в polling mode)...")

    try:
        result = await bot.delete_webhook(drop_pending_updates=False)
        if result:
            logger.info("✓ Webhook удалён, используется polling mode")
        else:
            logger.warning("Telegram вернул False при удалении webhook")
    except Exception:
        logger.exception("Ошибка при удалении webhook")
        # Не критично — продолжаем работу
