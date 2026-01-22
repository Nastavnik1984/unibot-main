"""Быстрая установка проекта для запуска отладки."""
import subprocess
import sys
import shutil
import venv
from pathlib import Path

ROOT = Path(__file__).parent
VENV = ROOT / ".venv"

print("=" * 50)
print("  БЫСТРАЯ УСТАНОВКА UNIBOT")
print("=" * 50)

# 1. Создание виртуального окружения
print("\n[1/4] Создание виртуального окружения...")
if VENV.exists():
    shutil.rmtree(VENV)
venv.EnvBuilder(with_pip=True).create(str(VENV))
print("✅ Виртуальное окружение создано")

# 2. Обновление pip
print("\n[2/4] Обновление pip...")
python = VENV / "Scripts" / "python.exe"
subprocess.run([str(python), "-m", "pip", "install", "--upgrade", "pip", "-q"], cwd=ROOT)
print("✅ pip обновлён")

# 3. Установка зависимостей
print("\n[3/4] Установка зависимостей (это займёт несколько минут)...")
pip = VENV / "Scripts" / "pip.exe"
result = subprocess.run([str(pip), "install", "-r", "requirements.txt"], cwd=ROOT)
if result.returncode == 0:
    print("✅ Основные зависимости установлены")
else:
    print("❌ Ошибка установки зависимостей")
    sys.exit(1)

subprocess.run([str(pip), "install", "-r", "requirements-dev.txt"], cwd=ROOT)
print("✅ Dev зависимости установлены")

# 4. Создание .env файла
print("\n[4/4] Настройка .env файла...")
env_file = ROOT / ".env"
env_example = ROOT / ".env.example"
if not env_file.exists() and env_example.exists():
    shutil.copy(env_example, env_file)
    print("✅ .env файл создан")
else:
    print("✅ .env файл уже существует")

# 5. Применение миграций
print("\n[5/5] Применение миграций...")
result = subprocess.run([str(python), "-m", "alembic", "upgrade", "head"], cwd=ROOT)
if result.returncode == 0:
    print("✅ Миграции применены")
else:
    print("⚠️ Миграции можно применить позже")

print("\n" + "=" * 50)
print("  ✅ УСТАНОВКА ЗАВЕРШЕНА!")
print("=" * 50)
print()
print("Теперь можно запустить отладку:")
print("  1. Нажмите F5 в VSCode/Cursor")
print("  2. Или: .venv\\Scripts\\activate.bat")
print("     Затем: uvicorn src.main:app --reload")
print()
print("⚠️ Не забудьте настроить .env файл!")
print("   BOT__TOKEN=ваш_токен_бота")
print()




