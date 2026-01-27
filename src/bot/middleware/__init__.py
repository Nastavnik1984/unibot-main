"""Middleware для Telegram-бота.

Middleware обрабатывают входящие события перед тем, как они попадут в handlers.
Используются для централизованной логики: аутентификация, логирование,
защита от спама, rate limiting.

Доступные middleware:
- PrivateChatMiddleware: Фильтрация сообщений только из личных чатов
- BannedUserMiddleware: Проверка забаненных пользователей (is_blocked в БД)
- create_banned_user_middleware: Factory function для создания BannedUserMiddleware
- GenerationCooldownMiddleware: Защита от спама генераций через cooldowns
- CooldownError: Исключение при нарушении cooldown
- LanguageMiddleware: Определение языка пользователя и создание Localization
- create_language_middleware: Factory function для создания LanguageMiddleware
- ChannelSubscriptionMiddleware: Проверка подписки на обязательный канал
- create_channel_subscription_middleware: Factory function для создания middleware
- CALLBACK_CHECK_SUBSCRIPTION: Константа callback_data для кнопки "Проверить подписку"
- LegalConsentMiddleware: Проверка согласия с юридическими документами
- create_legal_consent_middleware: Factory function для создания middleware
"""

from src.bot.middleware.banned_user import (
    BannedUserMiddleware,
    create_banned_user_middleware,
)
from src.bot.middleware.channel_subscription import (
    CALLBACK_CHECK_SUBSCRIPTION,
    ChannelSubscriptionMiddleware,
    create_channel_subscription_middleware,
)
from src.bot.middleware.cooldown import GenerationCooldownMiddleware
from src.bot.middleware.language import (
    LanguageMiddleware,
    create_language_middleware,
)
from src.bot.middleware.legal_consent import (
    LegalConsentMiddleware,
    create_legal_consent_middleware,
)
from src.bot.middleware.private_chat import PrivateChatMiddleware
from src.core.exceptions import CooldownError

__all__ = [
    "CALLBACK_CHECK_SUBSCRIPTION",
    "BannedUserMiddleware",
    "ChannelSubscriptionMiddleware",
    "CooldownError",
    "GenerationCooldownMiddleware",
    "LanguageMiddleware",
    "LegalConsentMiddleware",
    "PrivateChatMiddleware",
    "create_banned_user_middleware",
    "create_channel_subscription_middleware",
    "create_language_middleware",
    "create_legal_consent_middleware",
]
