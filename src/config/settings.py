"""Настройки приложения через переменные окружения.

ВАЖНО: Этот модуль загружает настройки из .env файла при импорте.
Для использования только классов настроек (без загрузки .env)
импортируйте из src.config.models вместо этого модуля.

Пример для тестов:
    # Изолированный импорт без побочных эффектов:
    from src.config.models import AIProvidersSettings

    # НЕ используйте в тестах (загрузит .env):
    from src.config.settings import AIProvidersSettings
"""

import sys
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Путь к корню проекта (вычисляем от текущего файла)
# src/config/settings.py → src/config → src → корень проекта
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Если файл .env существует — используем его, иначе None (только переменные окружения)
# Это нужно для Amvera и других облачных платформ, где секреты задаются
# через переменные окружения в панели управления, а не через файл .env
ENV_FILE_PATH = ENV_FILE if ENV_FILE.exists() else None

# Импортируем классы настроек из models.py
# Это позволяет тестам импортировать классы без побочных эффектов
from src.config.models import (
    AdminSettings,
    AIProvidersSettings,
    AppSettings,
    BotSettings,
    ChannelSettings,
    CORSSettings,
    DatabaseSettings,
    FSMSettings,
    LoggingSettings,
    PaymentsSettings,
    StripeSettings,
    TelegramLoggingSettings,
    TelegramStarsSettings,
    YooKassaSettings,
)

# Реэкспортируем классы для обратной совместимости
__all__ = [
    "AIProvidersSettings",
    "AdminSettings",
    "AppSettings",
    "BotSettings",
    "CORSSettings",
    "ChannelSettings",
    "DatabaseSettings",
    "FSMSettings",
    "LoggingSettings",
    "PaymentsSettings",
    "Settings",
    "StripeSettings",
    "TelegramLoggingSettings",
    "TelegramStarsSettings",
    "YooKassaSettings",
    "load_settings",
    "settings",
]

# ==============================================================================
# СЛОВАРЬ ОШИБОК НА РУССКОМ ЯЗЫКЕ
# ==============================================================================
#
# Pydantic выдаёт ошибки на английском. Здесь мы переводим их на русский,
# чтобы начинающему разработчику было понятно, что пошло не так.
#
# Ключ — название поля в формате "родитель.поле" (например, "bot.token")
# Значение — понятное описание ошибки и как её исправить

FIELD_ERROR_MESSAGES: dict[str, str] = {
    "bot": "Не указана переменная BOT__TOKEN (в файле .env или переменных окружения)",
    "bot.token": "Не указана переменная BOT__TOKEN (в файле .env или переменных окружения)",
}

# Сообщение по умолчанию для неизвестных полей
DEFAULT_ERROR_MESSAGE = "Ошибка конфигурации. Проверьте файл .env или переменные окружения"


class Settings(BaseSettings):
    """Главные настройки приложения.

    Настройки загружаются из двух источников (в порядке приоритета):
    1. Переменные окружения (приоритет выше)
    2. Файл .env (если существует)

    На локальной машине: используется файл .env
    На Amvera/облаке: переменные задаются в панели управления
    """

    model_config = SettingsConfigDict(
        # Если файл .env есть — читаем из него, если нет — только из переменных окружения
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app: AppSettings = AppSettings()
    bot: BotSettings
    database: DatabaseSettings = DatabaseSettings()
    logging: LoggingSettings = LoggingSettings()
    admin: AdminSettings = AdminSettings()
    ai: AIProvidersSettings = AIProvidersSettings()
    fsm: FSMSettings = FSMSettings()
    payments: PaymentsSettings = PaymentsSettings()
    channel: ChannelSettings = ChannelSettings()
    cors: CORSSettings = CORSSettings()

    # URL прокси-сервера для обхода блокировок (опционально).
    # Формат: http://host:port, https://host:port, socks5://host:port
    # Если указан — все HTTP-запросы к AI-провайдерам будут идти через прокси.
    # Если не указан — прямое подключение.
    # Пример: http://proxy.example.com:8080
    proxy: str | None = None


def _format_validation_error(error: ValidationError) -> str:
    """Преобразовать ошибку Pydantic в понятное русское сообщение.

    Args:
        error: Ошибка валидации от Pydantic.

    Returns:
        Понятное сообщение на русском языке.
    """
    messages: list[str] = []

    for err in error.errors():
        # Получаем путь к полю (например, ("bot", "token") -> "bot.token")
        field_path = ".".join(str(loc) for loc in err["loc"])

        # Ищем русское сообщение для этого поля
        if field_path in FIELD_ERROR_MESSAGES:
            messages.append(FIELD_ERROR_MESSAGES[field_path])
        else:
            messages.append(DEFAULT_ERROR_MESSAGE)
            messages.append(f"Поле: {field_path}")
            messages.append(f"Тип ошибки: {err['type']}")
            messages.append(f"Сообщение: {err['msg']}")

    return "\n".join(messages)


def load_settings() -> Settings:
    """Загрузить настройки из переменных окружения.

    Если настройки некорректны — выводит понятную ошибку на русском
    и завершает программу.

    Returns:
        Объект Settings с загруженными настройками.
    """
    import os

    # Отладка: показываем откуда читаются настройки
    env_file_exists = ENV_FILE.exists() if ENV_FILE else False
    bot_token_in_env = "BOT__TOKEN" in os.environ

    print(f"[DEBUG settings] CWD: {os.getcwd()}", file=sys.stderr)
    print(f"[DEBUG settings] ENV_FILE: {ENV_FILE}", file=sys.stderr)
    print(f"[DEBUG settings] ENV_FILE exists: {env_file_exists}", file=sys.stderr)
    print(f"[DEBUG settings] BOT__TOKEN in os.environ: {bot_token_in_env}", file=sys.stderr)

    try:
        result = Settings()
        print(f"[DEBUG settings] Токен загружен успешно!", file=sys.stderr)
        return result
    except ValidationError as e:
        # Выводим понятную ошибку на русском
        print(_format_validation_error(e), file=sys.stderr)
        sys.exit(1)


# Загружаем настройки при импорте модуля.
# Если .env не настроен — программа завершится с понятной ошибкой.
settings = load_settings()
