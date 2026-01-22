"""Проверка установки проекта."""
import sys
from pathlib import Path

project_root = Path(__file__).parent
venv_path = project_root / ".venv"
python_exe = venv_path / "Scripts" / "python.exe"
env_path = project_root / ".env"

print("=" * 60)
print("  ПРОВЕРКА УСТАНОВКИ")
print("=" * 60)
print()

# Проверка виртуального окружения
if venv_path.exists():
    print("✅ Виртуальное окружение создано")
else:
    print("❌ Виртуальное окружение не найдено")
    sys.exit(1)

# Проверка Python в venv
if python_exe.exists():
    print("✅ Python в виртуальном окружении найден")
else:
    print("❌ Python в виртуальном окружении не найден")
    sys.exit(1)

# Проверка зависимостей
print("\nПроверка зависимостей...")
try:
    sys.path.insert(0, str(venv_path / "Lib" / "site-packages"))
    import aiogram
    print("✅ aiogram установлен")
    import fastapi
    print("✅ fastapi установлен")
    import sqlalchemy
    print("✅ sqlalchemy установлен")
    import alembic
    print("✅ alembic установлен")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Зависимости не установлены полностью")
    sys.exit(1)

# Проверка .env
print("\nПроверка файла .env...")
if env_path.exists():
    print("✅ Файл .env существует")
    content = env_path.read_text(encoding="utf-8")
    if "BOT__TOKEN=" in content:
        for line in content.split("\n"):
            if line.startswith("BOT__TOKEN="):
                token = line.split("=", 1)[1].strip()
                if token and token != "ваш_токен_бота":
                    print("✅ BOT__TOKEN указан в .env")
                else:
                    print("⚠️  BOT__TOKEN не заполнен в .env")
else:
    print("⚠️  Файл .env не найден")
    env_example = project_root / ".env.example"
    if env_example.exists():
        print("Создаю .env из .env.example...")
        import shutil
        shutil.copy(env_example, env_path)
        print("✅ Файл .env создан")

print("\n" + "=" * 60)
print("  ✅ ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 60)
print("\nДля запуска бота:")
print("  .venv\\Scripts\\activate.bat")
print("  uvicorn src.main:app --reload")




