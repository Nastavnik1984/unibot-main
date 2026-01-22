"""Прямая установка проекта через Python API."""
import subprocess
import sys
import shutil
from pathlib import Path

project_root = Path(__file__).parent
venv_path = project_root / ".venv"
python_exe = venv_path / "Scripts" / "python.exe" if venv_path.exists() else None

print("=" * 60)
print("  УСТАНОВКА ПРОЕКТА UNIBOT")
print("=" * 60)
print()

# 1. Создание виртуального окружения
print("[1/5] Создание виртуального окружения...")
if not venv_path.exists():
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
    print("✅ Виртуальное окружение создано")
    python_exe = venv_path / "Scripts" / "python.exe"
else:
    print("✅ Виртуальное окружение уже существует")
    python_exe = venv_path / "Scripts" / "python.exe"

# 2. Обновление pip
print("\n[2/5] Обновление pip...")
subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "--quiet"], check=True)
print("✅ pip обновлён")

# 3. Установка зависимостей
print("\n[3/5] Установка зависимостей...")
print("Это может занять несколько минут...")
subprocess.run([str(python_exe), "-m", "pip", "install", "-r", str(project_root / "requirements.txt")], check=True, cwd=project_root)
subprocess.run([str(python_exe), "-m", "pip", "install", "-r", str(project_root / "requirements-dev.txt")], check=True, cwd=project_root)
print("✅ Все зависимости установлены")

# 4. Создание .env
print("\n[4/5] Создание файла .env...")
env_path = project_root / ".env"
env_example_path = project_root / ".env.example"
if not env_path.exists() and env_example_path.exists():
    shutil.copy(env_example_path, env_path)
    print("✅ Файл .env создан из .env.example")
    print("⚠️  ВАЖНО: Откройте .env и укажите BOT__TOKEN!")
elif env_path.exists():
    print("✅ Файл .env уже существует")
else:
    print("⚠️  Файл .env.example не найден")

# 5. Применение миграций
print("\n[5/5] Применение миграций...")
alembic_exe = venv_path / "Scripts" / "alembic.exe"
if alembic_exe.exists():
    try:
        subprocess.run([str(alembic_exe), "upgrade", "head"], check=True, cwd=project_root)
        print("✅ Миграции применены")
    except:
        print("⚠️  Ошибка применения миграций (это может быть нормально)")

print("\n" + "=" * 60)
print("  ✅ УСТАНОВКА ЗАВЕРШЕНА!")
print("=" * 60)
print("\nСледующие шаги:")
print("1. Откройте файл .env и укажите BOT__TOKEN")
print("2. Запустите бота: uvicorn src.main:app --reload")
print("\nАдминка: http://localhost:8000/admin\n")




