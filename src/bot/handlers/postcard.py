"""Обработчик команды /postcard — генерация праздничных открыток.

Этот модуль реализует создание открыток через AI:
- Загрузка фото пользователя (себя, семьи, друзей)
- Выбор праздника (Новый год, День рождения, 8 марта и др.)
- Ввод персонального текста поздравления (опционально)
- Генерация красивой открытки и отправка пользователю
"""

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    InaccessibleMessage,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.states.postcard import PostcardStates
from src.bot.utils.billing import charge_after_delivery, check_billing_and_show_error
from src.core.exceptions import GenerationError
from src.db.base import DatabaseSession
from src.db.exceptions import DatabaseError, UserNotFoundError
from src.db.repositories import UserRepository
from src.services.ai_service import AIService, create_ai_service
from src.services.billing_service import create_billing_service
from src.utils import create_input_file_from_url
from src.utils.i18n import Localization
from src.utils.logging import get_logger

# Команда для меню бота
COMMAND = BotCommand(command="postcard", description="🎴 Генератор открыток")

# Два роутера для правильного приоритета:
# - router: команды (высокий приоритет, регистрируется первым)
# - fsm_router: FSM handlers (низкий приоритет, регистрируется после команд)
router = Router(name="postcard")
fsm_router = Router(name="postcard_fsm")
logger = get_logger(__name__)

# Константа для типа генерации (используется для billing, cooldown, tracking)
GENERATION_TYPE_POSTCARD = "postcard"

# Модель по умолчанию для генерации открыток
DEFAULT_MODEL_KEY = "gemini-postcard"


@dataclass
class HolidayConfig:
    """Конфигурация праздника для генерации открытки."""

    emoji: str
    name_key: str
    prompt: str


@dataclass
class GenerationContext:
    """Контекст для генерации открытки."""

    message: Message
    state: FSMContext
    l10n: Localization
    greeting_text: str | None
    ai_service: AIService
    processing_msg: Message
    image_file_id: str
    holiday_id: str


# Базовый стиль для всех открыток — винтажный СССР
VINTAGE_USSR_STYLE = (
    "Style: vintage Soviet USSR postcard from 1960s-1980s. "
    "Use warm retro colors, slightly faded tones, soft watercolor effect. "
    "Add nostalgic Soviet aesthetics with hand-drawn illustration style. "
    "Make it look like a classic Soviet greeting card with artistic borders."
)

# Инструкция для AI — ОБЯЗАТЕЛЬНО использовать лицо с фото
PHOTO_INSTRUCTION = (
    "IMPORTANT: You MUST use the face/person from the uploaded photo as the "
    "main subject of this greeting card. Keep their face recognizable but "
    "transform them into the artistic style. Place them prominently on the card."
)

# Словарь праздников с их промптами для AI
HOLIDAYS: dict[str, HolidayConfig] = {
    "new_year": HolidayConfig(
        emoji="🎄",
        name_key="postcard_holiday_new_year",
        prompt=(
            f"{PHOTO_INSTRUCTION} "
            f"Create a vintage Soviet New Year greeting card featuring this "
            f"person. Add Ded Moroz elements around them, Soviet Christmas "
            f"tree with red star, snow, Kremlin clock. {VINTAGE_USSR_STYLE}"
        ),
    ),
    "birthday": HolidayConfig(
        emoji="🎂",
        name_key="postcard_holiday_birthday",
        prompt=(
            f"{PHOTO_INSTRUCTION} "
            f"Create a vintage Soviet birthday greeting card featuring this "
            f"person celebrating. Add retro balloons, Soviet-style cake with "
            f"candles, flowers around them. {VINTAGE_USSR_STYLE}"
        ),
    ),
    "march_8": HolidayConfig(
        emoji="💐",
        name_key="postcard_holiday_march_8",
        prompt=(
            f"{PHOTO_INSTRUCTION} "
            f"Create a vintage Soviet March 8 Women's Day card featuring this "
            f"person surrounded by mimosa flowers, tulips, spring branches, "
            f"decorative number 8. {VINTAGE_USSR_STYLE}"
        ),
    ),
    "mothers_day": HolidayConfig(
        emoji="🌸",
        name_key="postcard_holiday_mothers_day",
        prompt=(
            f"{PHOTO_INSTRUCTION} "
            f"Create a vintage Soviet Mother's Day card featuring this person "
            f"with soft flowers like carnations, roses, gentle warm lighting "
            f"in Soviet artistic tradition. {VINTAGE_USSR_STYLE}"
        ),
    ),
    "feb_23": HolidayConfig(
        emoji="💪",
        name_key="postcard_holiday_feb_23",
        prompt=(
            f"{PHOTO_INSTRUCTION} "
            f"Create a vintage Soviet February 23 Defender Day card featuring "
            f"this person with red stars, Soviet military symbols, laurel "
            f"branches around them. {VINTAGE_USSR_STYLE}"
        ),
    ),
    "valentines": HolidayConfig(
        emoji="💕",
        name_key="postcard_holiday_valentines",
        prompt=(
            f"{PHOTO_INSTRUCTION} "
            f"Create a vintage Soviet romantic greeting card featuring this "
            f"person with hearts, roses, doves around them in nostalgic USSR "
            f"postcard aesthetics. {VINTAGE_USSR_STYLE}"
        ),
    ),
    "universal": HolidayConfig(
        emoji="✨",
        name_key="postcard_holiday_universal",
        prompt=(
            f"{PHOTO_INSTRUCTION} "
            f"Create a beautiful vintage Soviet greeting card featuring this "
            f"person with elegant floral decorations, artistic frame around "
            f"them. {VINTAGE_USSR_STYLE}"
        ),
    ),
}


def create_holiday_keyboard(l10n: Localization) -> InlineKeyboardMarkup:
    """Создать клавиатуру выбора праздника."""
    buttons = []
    for holiday_id, config in HOLIDAYS.items():
        holiday_name = l10n.get(config.name_key)
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{config.emoji} {holiday_name}",
                    callback_data=f"postcard_holiday:{holiday_id}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_skip_greeting_keyboard(l10n: Localization) -> InlineKeyboardMarkup:
    """Создать клавиатуру с кнопкой 'Пропустить'."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=l10n.get("postcard_skip_greeting"),
                    callback_data="postcard_skip_greeting",
                )
            ]
        ]
    )


async def _download_image(bot: Bot, file_id: str) -> bytes | None:
    """Скачать изображение из Telegram по file_id."""
    file = await bot.get_file(file_id)
    if not file.file_path:
        return None

    image_bytes = await bot.download_file(file.file_path)
    if not image_bytes:
        return None

    return image_bytes.read()


def _build_prompt(holiday_id: str, greeting_text: str | None) -> str:
    """Сформировать промпт для AI на основе праздника и текста."""
    config = HOLIDAYS.get(holiday_id, HOLIDAYS["universal"])
    base_prompt = config.prompt

    if greeting_text:
        return (
            f"{base_prompt} "
            f'Add this greeting text in a beautiful font: "{greeting_text}"'
        )
    return base_prompt


async def _handle_generation_error(
    error: Exception,
    processing_msg: Message,
    l10n: Localization,
    state: FSMContext,
) -> None:
    """Обработать ошибку генерации открытки."""
    if isinstance(error, UserNotFoundError):
        await processing_msg.edit_text(l10n.get("error_user_not_found"))
    elif isinstance(error, GenerationError):
        # Проверяем, является ли это ошибкой "модель не сгенерировала изображение"
        error_message_lower = error.message.lower() if error.message else ""
        if "не сгенерировала" in error_message_lower or "не сгенерировало" in error_message_lower:
            # Специфичная ошибка для открыток - показываем более понятное сообщение
            await processing_msg.edit_text(
                "❌ Ошибка генерации открытки.\n\n"
                "Модель не смогла создать изображение. Возможные причины:\n"
                "• Фото слишком маленькое или нечёткое\n"
                "• На фото нет лица или оно плохо видно\n"
                "• Проблемы с API провайдера\n\n"
                "Попробуйте:\n"
                "• Загрузить другое фото (чёткое, с хорошо видимым лицом)\n"
                "• Попробовать ещё раз через несколько секунд\n"
                "• Выбрать другой праздник"
            )
        else:
            await processing_msg.edit_text(l10n.get("generation_error"))
        logger.error(
            "Ошибка генерации открытки: %s | provider=%s | model_id=%s",
            error.message,
            error.provider if hasattr(error, "provider") else "unknown",
            error.model_id if hasattr(error, "model_id") else "unknown",
        )
    elif isinstance(error, DatabaseError):
        key = "error_db_temporary" if error.retryable else "error_db_permanent"
        await processing_msg.edit_text(l10n.get(key))
    else:
        await processing_msg.edit_text(l10n.get("generation_unexpected_error"))
        logger.exception("Неожиданная ошибка при генерации открытки")

    await state.clear()


async def _send_postcard(
    message: Message,
    result_url: str,
    holiday_id: str,
    greeting_text: str | None,
    l10n: Localization,
) -> bool:
    """Отправить открытку пользователю. Возвращает True при успехе."""
    config = HOLIDAYS.get(holiday_id, HOLIDAYS["universal"])
    holiday_name = l10n.get(config.name_key)

    try:
        await message.answer_photo(
            photo=create_input_file_from_url(result_url),
            caption=l10n.get(
                "postcard_completed",
                holiday=f"{config.emoji} {holiday_name}",
                greeting=greeting_text or l10n.get("postcard_no_greeting"),
            ),
        )
        return True
    except Exception:
        if message.from_user:
            logger.exception(
                "Ошибка отправки открытки | user_id=%d | holiday=%s",
                message.from_user.id,
                holiday_id,
            )
        await message.answer(l10n.get("postcard_send_error"))
        return False


async def _generate_postcard(
    message: Message,
    state: FSMContext,
    l10n: Localization,
    greeting_text: str | None,
    ai_service: AIService | None,
    session_factory: Callable[[], AbstractAsyncContextManager[AsyncSession]],
) -> None:
    """Сгенерировать открытку и отправить пользователю."""
    if not message.from_user or not message.bot:
        return

    state_data = await state.get_data()
    image_file_id = state_data.get("image_file_id")
    holiday_id = state_data.get("holiday_id")

    if not image_file_id or not holiday_id:
        await message.answer(l10n.get("postcard_error_missing_data"))
        await state.clear()
        return

    if ai_service is None:
        ai_service = create_ai_service()

    processing_msg = await message.answer(l10n.get("postcard_processing"))

    ctx = GenerationContext(
        message=message,
        state=state,
        l10n=l10n,
        greeting_text=greeting_text,
        ai_service=ai_service,
        processing_msg=processing_msg,
        image_file_id=image_file_id,
        holiday_id=holiday_id,
    )

    try:
        async with session_factory() as session:
            await _execute_generation(ctx, session)
    except (UserNotFoundError, GenerationError, DatabaseError) as e:
        await _handle_generation_error(e, processing_msg, l10n, state)


async def _execute_generation(ctx: GenerationContext, session: AsyncSession) -> None:
    """Выполнить генерацию открытки (внутренняя логика)."""
    if not ctx.message.from_user or not ctx.message.bot:
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(ctx.message.from_user.id)
    if not user:
        raise UserNotFoundError(ctx.message.from_user.id)

    # Проверяем биллинг
    billing = create_billing_service(session)
    cost = await check_billing_and_show_error(
        billing, user, DEFAULT_MODEL_KEY, ctx.processing_msg, ctx.l10n
    )
    if cost is None:
        await ctx.state.clear()
        return

    # Скачиваем изображение
    image_data = await _download_image(ctx.message.bot, ctx.image_file_id)
    if not image_data:
        await ctx.processing_msg.edit_text(
            ctx.l10n.get("postcard_image_download_error")
        )
        await ctx.state.clear()
        return

    # Генерируем открытку
    final_prompt = _build_prompt(ctx.holiday_id, ctx.greeting_text)
    logger.debug("Генерация открытки: user_id=%d, holiday=%s", user.id, ctx.holiday_id)

    result = await ctx.ai_service.generate(
        model_key=DEFAULT_MODEL_KEY,
        prompt=final_prompt,
        image_data=image_data,
    )

    if not result.content or not isinstance(result.content, str):
        await ctx.processing_msg.edit_text(ctx.l10n.get("postcard_empty_response"))
        await ctx.state.clear()
        return

    # Удаляем сообщение "Создаю открытку..."
    await ctx.processing_msg.delete()

    # Отправляем открытку
    if not await _send_postcard(
        ctx.message, result.content, ctx.holiday_id, ctx.greeting_text, ctx.l10n
    ):
        await ctx.state.clear()
        return

    # Списываем токены после успешной отправки
    await charge_after_delivery(
        billing, user, DEFAULT_MODEL_KEY, cost, GENERATION_TYPE_POSTCARD
    )

    logger.info("Открытка создана: user_id=%d, holiday=%s", user.id, ctx.holiday_id)
    await ctx.state.clear()


@router.message(Command(COMMAND))
async def cmd_postcard(
    message: Message, state: FSMContext, l10n: Localization
) -> None:
    """Обработать команду /postcard — начать создание открытки."""
    if not message.from_user:
        return

    await state.set_state(PostcardStates.waiting_for_image)
    await message.answer(l10n.get("postcard_send_image"))
    logger.info(
        "Пользователь %d начал создание открытки /postcard", message.from_user.id
    )


@fsm_router.message(PostcardStates.waiting_for_image, F.photo)
async def handle_image_upload(
    message: Message,
    state: FSMContext,
    l10n: Localization,
) -> None:
    """Обработать загрузку фото от пользователя."""
    if not message.from_user or not message.photo:
        return

    photo = message.photo[-1]
    await state.update_data(image_file_id=photo.file_id)

    keyboard = create_holiday_keyboard(l10n)
    await state.set_state(PostcardStates.waiting_for_holiday_selection)
    await message.answer(l10n.get("postcard_choose_holiday"), reply_markup=keyboard)

    logger.info(
        "Пользователь %d загрузил фото для открытки: file_id=%s",
        message.from_user.id,
        photo.file_id,
    )


@fsm_router.message(
    PostcardStates.waiting_for_image,
    ~F.photo,
    ~F.text.startswith("/"),
)
async def handle_invalid_image(message: Message, l10n: Localization) -> None:
    """Обработать сообщение без фото в состоянии ожидания."""
    await message.answer(l10n.get("postcard_please_send_image"))


@fsm_router.callback_query(
    PostcardStates.waiting_for_holiday_selection,
    F.data.startswith("postcard_holiday:"),
)
async def handle_holiday_selection(
    callback: CallbackQuery,
    state: FSMContext,
    l10n: Localization,
) -> None:
    """Обработать выбор праздника пользователем."""
    if (
        not callback.data
        or not callback.message
        or isinstance(callback.message, InaccessibleMessage)
    ):
        return

    holiday_id = callback.data.split(":", 1)[1]

    if holiday_id not in HOLIDAYS:
        await callback.answer(l10n.get("error_callback_data"))
        return

    await state.update_data(holiday_id=holiday_id)

    config = HOLIDAYS[holiday_id]
    holiday_name = l10n.get(config.name_key)

    await state.set_state(PostcardStates.waiting_for_greeting_text)

    keyboard = create_skip_greeting_keyboard(l10n)
    await callback.message.edit_text(
        l10n.get("postcard_enter_greeting", holiday=f"{config.emoji} {holiday_name}"),
        reply_markup=keyboard,
    )
    await callback.answer()

    logger.info(
        "Пользователь %d выбрал праздник: %s",
        callback.from_user.id,
        holiday_id,
    )


@fsm_router.callback_query(
    PostcardStates.waiting_for_greeting_text,
    F.data == "postcard_skip_greeting",
)
async def handle_skip_greeting(
    callback: CallbackQuery,
    state: FSMContext,
    l10n: Localization,
    ai_service: AIService | None = None,
    session_factory: Callable[
        [], AbstractAsyncContextManager[AsyncSession]
    ] = DatabaseSession,
) -> None:
    """Обработать пропуск ввода текста поздравления."""
    if not callback.message or isinstance(callback.message, InaccessibleMessage):
        return

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await _generate_postcard(
        message=callback.message,
        state=state,
        l10n=l10n,
        greeting_text=None,
        ai_service=ai_service,
        session_factory=session_factory,
    )


@fsm_router.message(
    PostcardStates.waiting_for_greeting_text,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_greeting_text(
    message: Message,
    state: FSMContext,
    l10n: Localization,
    ai_service: AIService | None = None,
    session_factory: Callable[
        [], AbstractAsyncContextManager[AsyncSession]
    ] = DatabaseSession,
) -> None:
    """Обработать текст поздравления от пользователя."""
    if not message.from_user or not message.text:
        return

    greeting_text = message.text[:500]

    logger.info(
        "Пользователь %d ввёл текст поздравления: %s",
        message.from_user.id,
        greeting_text[:50],
    )

    await _generate_postcard(
        message=message,
        state=state,
        l10n=l10n,
        greeting_text=greeting_text,
        ai_service=ai_service,
        session_factory=session_factory,
    )
