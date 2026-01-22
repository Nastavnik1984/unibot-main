# -*- coding: utf-8 -*-
"""Скрипт для настройки базы данных и применения миграций.

Этот скрипт выполняет:
1. Проверку виртуального окружения
2. Установку зависимостей (если нужно)
3. Применение миграций Alembic

Запуск:
    python setup_database.py

Или через виртуальное окружение:
    .venv\Scripts\python.exe setup_database.py
"""

import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Получить корневую папку проекта."""
    return Path(__file__).parent


def get_venv_python() -> Path:
    """Получить путь к Python в виртуальном окружении."""
    root = get_project_root()
    if sys.platform == "win32":
        return root / ".venv" / "Scripts" / "python.exe"
    return root / ".venv" / "bin" / "python"


def get_venv_pip() -> Path:
    """Получить путь к pip в виртуальном окружении."""
    root = get_project_root()
    if sys.platform == "win32":
        return root / ".venv" / "Scripts" / "pip.exe"
    return root / ".venv" / "bin" / "pip"


def create_venv() -> bool:
    """Создать виртуальное окружение если его нет."""
    root = get_project_root()
    venv_path = root / ".venv"
    
    if venv_path.exists():
        print(f"✅ Виртуальное окружение уже существует: {venv_path}")
        return True
    
    print("📦 Создание виртуального окружения...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            cwd=str(root)
        )
        print(f"✅ Виртуальное окружение создано: {venv_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании venv: {e}")
        return False


def install_dependencies() -> bool:
    """Установить зависимости из requirements.txt."""
    root = get_project_root()
    pip_path = get_venv_pip()
    requirements_path = root / "requirements.txt"
    
    if not pip_path.exists():
        print(f"❌ pip не найден: {pip_path}")
        return False
    
    if not requirements_path.exists():
        print(f"❌ requirements.txt не найден: {requirements_path}")
        return False
    
    print("📦 Установка зависимостей...")
    try:
        # Сначала обновляем pip
        subprocess.run(
            [str(pip_path), "install", "--upgrade", "pip", "--quiet"],
            check=True,
            cwd=str(root)
        )
        
        # Устанавливаем зависимости
        subprocess.run(
            [str(pip_path), "install", "-r", str(requirements_path), "--quiet"],
            check=True,
            cwd=str(root)
        )
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке зависимостей: {e}")
        return False


def check_alembic_installed() -> bool:
    """Проверить, установлен ли Alembic."""
    python_path = get_venv_python()
    
    try:
        result = subprocess.run(
            [str(python_path), "-c", "import alembic; print(alembic.__version__)"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Alembic установлен: v{result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Alembic не установлен")
        return False


def run_migrations() -> bool:
    """Применить миграции Alembic."""
    root = get_project_root()
    python_path = get_venv_python()
    
    print("🔄 Применение миграций базы данных...")
    
    try:
        # Запускаем alembic upgrade head через Python
        result = subprocess.run(
            [str(python_path), "-m", "alembic", "upgrade", "head"],
            check=True,
            cwd=str(root),
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            # Alembic выводит INFO в stderr
            print(result.stderr)
            
        print("✅ Миграции успешно применены!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при применении миграций:")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def check_database_exists() -> bool:
    """Проверить существование файла базы данных."""
    root = get_project_root()
    db_path = root / "data" / "bot.db"
    
    if db_path.exists():
        size_kb = db_path.stat().st_size / 1024
        print(f"✅ База данных существует: {db_path} ({size_kb:.1f} KB)")
        return True
    else:
        print(f"ℹ️  База данных будет создана: {db_path}")
        return False


def ensure_data_dir() -> None:
    """Создать папку data если её нет."""
    root = get_project_root()
    data_dir = root / "data"
    
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        print(f"📁 Создана папка: {data_dir}")


def main() -> int:
    """Главная функция."""
    print("=" * 60)
    print("🗄️  НАСТРОЙКА БАЗЫ ДАННЫХ UNIBOT")
    print("=" * 60)
    print()
    
    root = get_project_root()
    print(f"📍 Папка проекта: {root}")
    print()
    
    # Шаг 1: Создаём папку data
    ensure_data_dir()
    
    # Шаг 2: Проверяем/создаём venv
    if not create_venv():
        return 1
    
    # Шаг 3: Устанавливаем зависимости
    if not install_dependencies():
        return 1
    
    # Шаг 4: Проверяем Alembic
    if not check_alembic_installed():
        print("⚠️  Попробуйте переустановить зависимости")
        return 1
    
    # Шаг 5: Проверяем существование БД
    check_database_exists()
    
    # Шаг 6: Применяем миграции
    print()
    if not run_migrations():
        return 1
    
    print()
    print("=" * 60)
    print("✅ НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 60)
    print()
    print("База данных готова к использованию.")
    print()
    print("Для запуска бота выполните:")
    print("  .venv\\Scripts\\python.exe -m uvicorn src.main:app --reload")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())




