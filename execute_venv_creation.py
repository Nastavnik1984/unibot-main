"""Выполнение создания виртуального окружения."""
import venv
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent
venv_path = root / ".venv"

print("=" * 60)
print("  СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ")
print("=" * 60)
print()

# Удаляем старое окружение
if venv_path.exists():
    print("[1/3] Удаление старого окружения...")
    try:
        shutil.rmtree(venv_path)
        print("✅ Старое окружение удалено")
    except Exception as e:
        print(f"⚠️  Ошибка удаления: {e}")
        print("Продолжаю...")
else:
    print("[1/3] Старое окружение не найдено")

print()
print("[2/3] Создание нового виртуального окружения...")
try:
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(str(venv_path))
    print("✅ Виртуальное окружение создано")
except Exception as e:
    print(f"❌ Ошибка создания: {e}")
    sys.exit(1)

print()
print("[3/3] Проверка созданного окружения...")
python_exe = venv_path / "Scripts" / "python.exe"
if python_exe.exists():
    try:
        result = subprocess.run(
            [str(python_exe), "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Проверка пройдена: {result.stdout.strip()}")
        else:
            print("⚠️  Окружение создано, но проверка не прошла")
    except Exception as e:
        print(f"⚠️  Ошибка проверки: {e}")
else:
    print("❌ python.exe не найден в окружении")
    sys.exit(1)

print()
print("=" * 60)
print("  ✅ ВИРТУАЛЬНОЕ ОКРУЖЕНИЕ СОЗДАНО!")
print("=" * 60)
print()
print("Следующие шаги:")
print("1. Активируйте окружение:")
print("   .venv\\Scripts\\activate.bat")
print()
print("2. Обновите pip:")
print("   python -m pip install --upgrade pip")
print()
print("3. Установите зависимости:")
print("   pip install -r requirements.txt")
print("   pip install -r requirements-dev.txt")
print()
print("4. Примените миграции:")
print("   alembic upgrade head")
print()
print("5. Запустите бота:")
print("   uvicorn src.main:app --reload")
print()




