"""Middleware для проверки забаненных пользователей.

Если пользователь забанен (is_blocked=True в БД), бот отвечает
сообщением "Вы забанены" и не пропускает событие дальше.

Забанить пользователя можно в админке:
1. Открыть пользователя → редактировать → is_blocked = True
2. Или использовать кнопки "Забанить/Разбанить" в списке пользователей

Пример использования:
    from src.bot.middleware.banned_user import create_banned_user_middleware

    middleware = create_banned_user_middleware()
    dp.message.middleware(middleware)
    dp.callback_query.middleware(middleware)
"""

from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Protocol

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User
from sqlalchemy.exc import SQLAlchemyError
from typing_extensions import override

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.user_repo import UserRepository
from src.utils.logging import get_logger

# Алиас для читаемости
AsyncContextManager = AbstractAsyncContextManager

logger = get_logger(__name__)

# Сообщение для забаненных пользователей
BANNED_MESSAGE = "🚫 Вы забанены"


class SessionFactory(Protocol):
    """Протокол для фабрики сессий БД (для Dependency Injection).

    Позволяет инжектировать mock session factory в тестах.
    """

    def __call__(self) -> "AsyncContextManager[AsyncSession]":
        """Создать асинхронный контекстный менеджер для сессии БД."""
        ...


class BannedUserMiddleware(BaseMiddleware):
    """Middleware для проверки забаненных пользователей.

    Проверяет поле is_blocked в модели User. Если True — отвечает
    сообщением "Вы забанены" и прерывает обработку события.

    Как это работает (как для 5-классника):
    1. Пользователь отправляет сообщение боту
    2. Middleware получает telegram_id пользователя
    3. Ищет пользователя в базе данных
    4. Если is_blocked=True → отвечает "Вы забанены" и СТОП
    5. Если is_blocked=False → пропускает событие дальше

    Attributes:
        _session_factory: Фабрика для создания сессий БД.
    """

    def __init__(self, session_factory: SessionFactory) -> None:
        """Создать middleware с инжектированной фабрикой сессий.

        Args:
            session_factory: Фабрика для создания сессий БД.
        """
        super().__init__()
        self._session_factory = session_factory

    @override
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, object]], Awaitable[object]],
        event: TelegramObject,
        data: dict[str, object],
    ) -> object:
        """Проверить, забанен ли пользователь.

        Args:
            handler: Следующий обработчик в цепочке.
            event: Событие от Telegram (Message, CallbackQuery и т.д.)
            data: Словарь данных для передачи в обработчик.

        Returns:
            Результат вызова следующего обработчика или None если забанен.
        """
        # Получаем telegram user из события
        # aiogram автоматически добавляет event_from_user в data
        telegram_user: User | None = data.get("event_from_user")  # type: ignore[assignment]

        if telegram_user is None:
            # Событие без пользователя — пропускаем дальше
            return await handler(event, data)

        # Проверяем, забанен ли пользователь
        is_banned = await self._is_user_banned(telegram_user.id)

        if is_banned:
            # Отправляем сообщение о бане
            await self._send_banned_message(event)
            # Не пропускаем событие дальше — возвращаем None
            return None

        # Пользователь не забанен — пропускаем событие дальше
        return await handler(event, data)

    async def _is_user_banned(self, telegram_id: int) -> bool:
        """Проверить, забанен ли пользователь в БД.

        Args:
            telegram_id: ID пользователя в Telegram.

        Returns:
            True если пользователь забанен, False иначе.
        """
        try:
            async with self._session_factory() as session:
                repo = UserRepository(session)
                user = await repo.get_by_telegram_id(telegram_id)

                # Если пользователь найден и is_blocked=True — забанен
                if user is not None and user.is_blocked:
                    logger.debug(
                        "Забаненный пользователь %d пытается использовать бота",
                        telegram_id,
                    )
                    return True

        except SQLAlchemyError:
            # Ошибка БД — не баним (на всякий случай)
            logger.exception(
                "Ошибка проверки бана пользователя %d в БД",
                telegram_id,
            )

        except OSError:
            # Ошибки сети/файловой системы
            logger.exception(
                "Ошибка подключения к БД при проверке бана пользователя %d",
                telegram_id,
            )

        return False

    async def _send_banned_message(self, event: TelegramObject) -> None:
        """Отправить сообщение о бане пользователю.

        Args:
            event: Событие от Telegram (Message или CallbackQuery).
        """
        try:
            if isinstance(event, Message):
                await event.answer(BANNED_MESSAGE)

            elif isinstance(event, CallbackQuery):
                # Для callback_query отвечаем через answer (popup)
                # и отправляем сообщение в чат
                await event.answer(BANNED_MESSAGE, show_alert=True)

        except Exception:
            # Не падаем если не получилось отправить сообщение
            logger.exception("Не удалось отправить сообщение о бане")


def create_banned_user_middleware() -> BannedUserMiddleware:
    """Создать BannedUserMiddleware с production зависимостями.

    Это основной способ создания middleware в production коде.
    Использует реальный DatabaseSession.

    Returns:
        Настроенный BannedUserMiddleware.

    Example:
        middleware = create_banned_user_middleware()
        dp.message.middleware(middleware)
        dp.callback_query.middleware(middleware)
    """
    # Импортируем здесь, чтобы избежать циклических импортов
    from src.db.base import DatabaseSession

    return BannedUserMiddleware(session_factory=DatabaseSession)




