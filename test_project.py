#!/usr/bin/env python3
"""Скрипт для проверки готовности проекта к запуску.

Проверяет:
- Наличие Python 3.11
- Наличие виртуального окружения
- Установленные зависимости
- Наличие файла .env
- Синтаксис кода
- Импорты основных модулей
"""

import sys
import subprocess
from pathlib import Path

# Цвета для вывода
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_success(message: str) -> None:
    """Выводит сообщение об успехе."""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message: str) -> None:
    """Выводит сообщение об ошибке."""
    print(f"{RED}❌ {message}{RESET}")


def print_warning(message: str) -> None:
    """Выводит предупреждение."""
    print(f"{YELLOW}⚠️  {message}{RESET}")


def print_info(message: str) -> None:
    """Выводит информационное сообщение."""
    print(f"{BLUE}ℹ️  {message}{RESET}")


def check_python_version() -> bool:
    """Проверяет версию Python."""
    print_info("Проверка версии Python...")
    version = sys.version_info
    if version.major == 3 and version.minor == 11:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Требуется Python 3.11, найдена версия {version.major}.{version.minor}.{version.micro}")
        return False


def check_venv() -> bool:
    """Проверяет наличие виртуального окружения."""
    print_info("Проверка виртуального окружения...")
    venv_path = Path(".venv")
    if venv_path.exists():
        print_success("Виртуальное окружение .venv найдено")
        return True
    else:
        print_warning("Виртуальное окружение .venv не найдено")
        print_info("Запустите: python -m venv .venv")
        return False


def check_dependencies() -> bool:
    """Проверяет установленные зависимости."""
    print_info("Проверка зависимостей...")
    required_modules = [
        "aiogram",
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "pydantic_settings",
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print_success(f"Модуль {module} установлен")
        except ImportError:
            print_error(f"Модуль {module} не установлен")
            missing.append(module)
    
    if missing:
        print_warning(f"Отсутствуют модули: {', '.join(missing)}")
        print_info("Запустите: pip install -r requirements.txt -r requirements-dev.txt")
        return False
    
    return True


def check_env_file() -> bool:
    """Проверяет наличие файла .env."""
    print_info("Проверка файла .env...")
    env_path = Path(".env")
    if env_path.exists():
        print_success("Файл .env найден")
        
        # Проверяем наличие токена
        try:
            content = env_path.read_text(encoding="utf-8")
            if "BOT__TOKEN=" in content:
                # Проверяем, что токен не пустой
                lines = content.split("\n")
                for line in lines:
                    if line.startswith("BOT__TOKEN="):
                        token = line.split("=", 1)[1].strip()
                        if token and token != "ваш_токен_бота":
                            print_success("BOT__TOKEN указан в .env")
                            return True
                        else:
                            print_warning("BOT__TOKEN не заполнен в .env")
                            return False
        except Exception as e:
            print_warning(f"Ошибка чтения .env: {e}")
        
        return True
    else:
        print_warning("Файл .env не найден")
        env_example = Path(".env.example")
        if env_example.exists():
            print_info("Создайте .env из .env.example: copy .env.example .env")
        return False


def check_syntax() -> bool:
    """Проверяет синтаксис основных файлов."""
    print_info("Проверка синтаксиса кода...")
    main_files = [
        "src/main.py",
        "src/config/settings.py",
        "src/app/factory.py",
    ]
    
    errors = []
    for file_path in main_files:
        path = Path(file_path)
        if not path.exists():
            print_warning(f"Файл {file_path} не найден")
            continue
        
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            print_success(f"Синтаксис {file_path} корректен")
        except SyntaxError as e:
            print_error(f"Синтаксическая ошибка в {file_path}: {e}")
            errors.append(file_path)
    
    return len(errors) == 0


def check_imports() -> bool:
    """Проверяет возможность импорта основных модулей."""
    print_info("Проверка импортов...")
    
    # Добавляем корень проекта в sys.path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    modules_to_check = [
        "src.config.models",
        "src.db.base",
        "src.app.factory",
    ]
    
    errors = []
    for module in modules_to_check:
        try:
            __import__(module)
            print_success(f"Модуль {module} импортируется")
        except Exception as e:
            print_error(f"Ошибка импорта {module}: {e}")
            errors.append(module)
    
    return len(errors) == 0


def check_migrations() -> bool:
    """Проверяет наличие миграций."""
    print_info("Проверка миграций...")
    migrations_path = Path("alembic/versions")
    if migrations_path.exists():
        migration_files = list(migrations_path.glob("*.py"))
        if migration_files:
            print_success(f"Найдено {len(migration_files)} файлов миграций")
            return True
        else:
            print_warning("Папка миграций пуста")
            return False
    else:
        print_warning("Папка миграций не найдена")
        return False


def main() -> None:
    """Главная функция проверки."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  ПРОВЕРКА ПРОЕКТА UNIBOT{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    checks = [
        ("Версия Python", check_python_version),
        ("Виртуальное окружение", check_venv),
        ("Зависимости", check_dependencies),
        ("Файл .env", check_env_file),
        ("Синтаксис кода", check_syntax),
        ("Импорты модулей", check_imports),
        ("Миграции", check_migrations),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{BLUE}[{name}]{RESET}")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Ошибка при проверке {name}: {e}")
            results.append((name, False))
    
    # Итоги
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  ИТОГИ ПРОВЕРКИ{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅{RESET}" if result else f"{RED}❌{RESET}"
        print(f"{status} {name}")
    
    print(f"\n{BLUE}Пройдено проверок: {passed}/{total}{RESET}\n")
    
    if passed == total:
        print_success("Все проверки пройдены! Проект готов к запуску.")
        print_info("Запустите: uvicorn src.main:app --reload")
        return 0
    else:
        print_warning("Некоторые проверки не пройдены.")
        print_info("Исправьте ошибки и запустите проверку снова.")
        return 1


if __name__ == "__main__":
    sys.exit(main())




