"""
Полная установка проекта Unibot по инструкции из README.md

Этот скрипт выполняет:
1. Проверку Python
2. Создание виртуального окружения
3. Установку всех зависимостей
4. Создание .env файла из .env.example
5. Применение миграций базы данных

Запуск: python ПОЛНАЯ_УСТАНОВКА.py
"""
import subprocess
import sys
import shutil
import venv
from pathlib import Path

# Путь к корню проекта
ROOT = Path(__file__).parent
VENV_PATH = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"
REQUIREMENTS_DEV = ROOT / "requirements-dev.txt"
ENV_EXAMPLE = ROOT / ".env.example"
ENV_FILE = ROOT / ".env"

def print_header(text: str) -> None:
    """Печать заголовка."""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)
    print()

def print_step(step: int, total: int, text: str) -> None:
    """Печать шага."""
    print(f"[{step}/{total}] {text}")

def check_python() -> tuple[bool, str]:
    """Проверка версии Python."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    # Проект требует Python 3.11+
    if version.major >= 3 and version.minor >= 11:
        return True, version_str
    else:
        return False, version_str

def create_venv() -> bool:
    """Создание виртуального окружения."""
    try:
        # Удаляем старое окружение, если есть
        if VENV_PATH.exists():
            print("   Удаление старого виртуального окружения...")
            shutil.rmtree(VENV_PATH)
        
        # Создаём новое окружение
        print("   Создание нового виртуального окружения...")
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(VENV_PATH))
        
        # Проверяем, что python.exe создан
        python_exe = VENV_PATH / "Scripts" / "python.exe"
        if python_exe.exists():
            return True
        else:
            print("   ❌ python.exe не найден в виртуальном окружении")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка создания виртуального окружения: {e}")
        return False

def get_venv_python() -> Path:
    """Получение пути к Python в виртуальном окружении."""
    return VENV_PATH / "Scripts" / "python.exe"

def get_venv_pip() -> Path:
    """Получение пути к pip в виртуальном окружении."""
    return VENV_PATH / "Scripts" / "pip.exe"

def upgrade_pip() -> bool:
    """Обновление pip."""
    try:
        python_exe = get_venv_python()
        result = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            cwd=ROOT
        )
        return result.returncode == 0
    except Exception as e:
        print(f"   ⚠️ Ошибка обновления pip: {e}")
        return False

def install_requirements() -> bool:
    """Установка зависимостей."""
    pip_exe = get_venv_pip()
    
    try:
        # Установка основных зависимостей
        print("   Установка основных зависимостей (requirements.txt)...")
        result = subprocess.run(
            [str(pip_exe), "install", "-r", str(REQUIREMENTS)],
            capture_output=True,
            text=True,
            cwd=ROOT
        )
        if result.returncode != 0:
            print(f"   ❌ Ошибка установки requirements.txt:")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
        
        # Установка dev зависимостей
        print("   Установка dev зависимостей (requirements-dev.txt)...")
        result = subprocess.run(
            [str(pip_exe), "install", "-r", str(REQUIREMENTS_DEV)],
            capture_output=True,
            text=True,
            cwd=ROOT
        )
        if result.returncode != 0:
            print(f"   ⚠️ Ошибка установки requirements-dev.txt (не критично)")
            # Продолжаем, dev-зависимости не обязательны
        
        return True
    except Exception as e:
        print(f"   ❌ Ошибка установки зависимостей: {e}")
        return False

def create_env_file() -> bool:
    """Создание .env файла из .env.example."""
    try:
        if ENV_FILE.exists():
            print("   .env файл уже существует")
            return True
        
        if not ENV_EXAMPLE.exists():
            print("   ⚠️ Файл .env.example не найден")
            return False
        
        # Копируем .env.example в .env
        shutil.copy(ENV_EXAMPLE, ENV_FILE)
        print("   .env файл создан из .env.example")
        return True
    except Exception as e:
        print(f"   ❌ Ошибка создания .env файла: {e}")
        return False

def run_migrations() -> bool:
    """Применение миграций базы данных."""
    try:
        python_exe = get_venv_python()
        
        # Запускаем alembic upgrade head
        result = subprocess.run(
            [str(python_exe), "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=ROOT
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"   ⚠️ Ошибка миграций (можно применить позже):")
            print(result.stderr[-300:] if len(result.stderr) > 300 else result.stderr)
            return False
    except Exception as e:
        print(f"   ⚠️ Ошибка миграций: {e}")
        return False

def verify_installation() -> bool:
    """Проверка установки."""
    try:
        python_exe = get_venv_python()
        
        # Проверяем aiogram
        result = subprocess.run(
            [str(python_exe), "-c", "import aiogram; print(f'aiogram {aiogram.__version__}')"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"   ✅ {result.stdout.strip()}")
        else:
            print("   ❌ aiogram не установлен")
            return False
        
        # Проверяем fastapi
        result = subprocess.run(
            [str(python_exe), "-c", "import fastapi; print(f'fastapi {fastapi.__version__}')"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"   ✅ {result.stdout.strip()}")
        else:
            print("   ❌ fastapi не установлен")
            return False
        
        # Проверяем sqlalchemy
        result = subprocess.run(
            [str(python_exe), "-c", "import sqlalchemy; print(f'sqlalchemy {sqlalchemy.__version__}')"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"   ✅ {result.stdout.strip()}")
        
        return True
    except Exception as e:
        print(f"   ⚠️ Ошибка проверки: {e}")
        return False

def main():
    """Главная функция установки."""
    print_header("ПОЛНАЯ УСТАНОВКА ПРОЕКТА UNIBOT")
    
    total_steps = 6
    
    # Шаг 1: Проверка Python
    print_step(1, total_steps, "Проверка Python...")
    ok, version = check_python()
    if ok:
        print(f"   ✅ Python {version} (совместим с проектом)")
    else:
        print(f"   ⚠️ Python {version} (рекомендуется 3.11+)")
        print("   Продолжаю установку с текущей версией...")
    
    # Шаг 2: Создание виртуального окружения
    print()
    print_step(2, total_steps, "Создание виртуального окружения...")
    if create_venv():
        print("   ✅ Виртуальное окружение создано")
    else:
        print("   ❌ Не удалось создать виртуальное окружение")
        return False
    
    # Шаг 3: Обновление pip
    print()
    print_step(3, total_steps, "Обновление pip...")
    if upgrade_pip():
        print("   ✅ pip обновлён")
    else:
        print("   ⚠️ Не удалось обновить pip, продолжаю...")
    
    # Шаг 4: Установка зависимостей
    print()
    print_step(4, total_steps, "Установка зависимостей...")
    print("   Это может занять несколько минут...")
    if install_requirements():
        print("   ✅ Зависимости установлены")
    else:
        print("   ❌ Ошибка установки зависимостей")
        return False
    
    # Шаг 5: Создание .env файла
    print()
    print_step(5, total_steps, "Настройка .env файла...")
    if create_env_file():
        print("   ✅ .env файл готов")
    else:
        print("   ⚠️ .env файл нужно создать вручную")
    
    # Шаг 6: Применение миграций
    print()
    print_step(6, total_steps, "Применение миграций базы данных...")
    if run_migrations():
        print("   ✅ Миграции применены")
    else:
        print("   ⚠️ Миграции можно применить позже командой: alembic upgrade head")
    
    # Проверка установки
    print()
    print("Проверка установки...")
    verify_installation()
    
    # Итог
    print_header("✅ УСТАНОВКА ЗАВЕРШЕНА!")
    
    print("Следующие шаги:")
    print()
    print("1. Настройте .env файл:")
    print("   - Откройте файл .env")
    print("   - Укажите BOT__TOKEN=ваш_токен_бота")
    print("   - (Опционально) Укажите AI__ROUTERAI_API_KEY для генераций")
    print()
    print("2. Активируйте виртуальное окружение:")
    print("   .venv\\Scripts\\activate.bat")
    print()
    print("3. Запустите бота:")
    print("   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("4. Проверьте работу:")
    print("   - Админка: http://localhost:8000/admin")
    print("   - Health check: http://localhost:8000/health")
    print("   - Напишите /start в Telegram")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print()
            print("❌ Установка завершена с ошибками")
            print("Проверьте вывод выше для диагностики")
        input("\nНажмите Enter для выхода...")
    except KeyboardInterrupt:
        print("\n\nУстановка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        input("\nНажмите Enter для выхода...")




