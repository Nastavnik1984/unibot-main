#!/usr/bin/env python3
"""Скрипт автоматической установки проекта Unibot."""

import subprocess
import sys
from pathlib import Path

# Цвета для вывода
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_step(step: int, total: int, message: str) -> None:
    """Выводит информацию о шаге."""
    print(f"{BLUE}[{step}/{total}]{RESET} {message}")


def print_success(message: str) -> None:
    """Выводит сообщение об успехе."""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message: str) -> None:
    """Выводит сообщение об ошибке."""
    print(f"{RED}❌ {message}{RESET}")


def run_command(cmd: list[str], cwd: Path | None = None) -> bool:
    """Выполняет команду и возвращает True если успешно."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout, end="")
        return True
    except subprocess.CalledProcessError as e:
        if e.stdout:
            print(e.stdout, end="")
        if e.stderr:
            print(e.stderr, end="", file=sys.stderr)
        return False


def main() -> int:
    """Главная функция установки."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  УСТАНОВКА ПРОЕКТА UNIBOT{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    # Определяем корень проекта
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv"
    python_exe = venv_path / "Scripts" / "python.exe"
    pip_exe = venv_path / "Scripts" / "pip.exe"

    # [1/6] Проверка Python
    print_step(1, 6, "Проверка Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    else:
        print_error(f"Требуется Python 3.11+, найдена версия {version.major}.{version.minor}.{version.micro}")
        return 1

    # [2/6] Проверка виртуального окружения
    print_step(2, 6, "Проверка виртуального окружения...")
    if not venv_path.exists():
        print("Создание виртуального окружения...")
        if not run_command([sys.executable, "-m", "venv", str(venv_path)]):
            print_error("Ошибка создания виртуального окружения")
            return 1
        print_success("Виртуальное окружение создано")
    else:
        print_success("Виртуальное окружение уже существует")

    # [3/6] Обновление pip
    print_step(3, 6, "Обновление pip...")
    if not run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "--quiet"]):
        print_error("Ошибка обновления pip")
        return 1
    print_success("pip обновлён")

    # [4/6] Установка зависимостей
    print_step(4, 6, "Установка зависимостей...")
    print("Это может занять несколько минут...")
    
    requirements_txt = project_root / "requirements.txt"
    requirements_dev_txt = project_root / "requirements-dev.txt"
    
    if not requirements_txt.exists():
        print_error(f"Файл {requirements_txt} не найден")
        return 1
    
    if not run_command([str(pip_exe), "install", "-r", str(requirements_txt)], cwd=project_root):
        print_error("Ошибка установки зависимостей из requirements.txt")
        return 1
    
    if requirements_dev_txt.exists():
        if not run_command([str(pip_exe), "install", "-r", str(requirements_dev_txt)], cwd=project_root):
            print_error("Ошибка установки зависимостей из requirements-dev.txt")
            return 1
    
    print_success("Все зависимости установлены")

    # [5/6] Создание .env файла
    print_step(5, 6, "Настройка файла .env...")
    env_path = project_root / ".env"
    env_example_path = project_root / ".env.example"
    
    if env_path.exists():
        print_success("Файл .env уже существует")
    else:
        if env_example_path.exists():
            import shutil
            shutil.copy(env_example_path, env_path)
            print_success("Файл .env создан из .env.example")
            print(f"{YELLOW}⚠️  ВАЖНО: Откройте .env и укажите BOT__TOKEN!{RESET}")
        else:
            print_error("Файл .env.example не найден")

    # [6/6] Применение миграций
    print_step(6, 6, "Применение миграций базы данных...")
    alembic_exe = venv_path / "Scripts" / "alembic.exe"
    
    if alembic_exe.exists():
        if not run_command([str(alembic_exe), "upgrade", "head"], cwd=project_root):
            print(f"{YELLOW}⚠️  Ошибка применения миграций (это может быть нормально){RESET}")
        else:
            print_success("Миграции применены")
    else:
        print(f"{YELLOW}⚠️  Alembic не найден, миграции будут применены при первом запуске{RESET}")

    # Итоги
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{GREEN}  ✅ УСТАНОВКА ЗАВЕРШЕНА!{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    print(f"{YELLOW}Следующие шаги:{RESET}")
    print("1. Откройте файл .env и укажите BOT__TOKEN")
    print("2. Запустите бота:")
    print(f"   {BLUE}uvicorn src.main:app --reload{RESET}")
    print("   или нажмите F5 в VSCode")
    print("\nАдминка будет доступна по адресу:")
    print(f"{BLUE}http://localhost:8000/admin{RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())




