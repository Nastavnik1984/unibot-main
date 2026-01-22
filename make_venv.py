"""Создание виртуального окружения через Python API."""
import venv
import sys
import shutil
from pathlib import Path

root = Path(__file__).parent
venv_path = root / ".venv"

print("Создание виртуального окружения...")

# Удаляем старое
if venv_path.exists():
    print("Удаление старого окружения...")
    shutil.rmtree(venv_path)

# Создаём новое
print("Создание нового окружения...")
builder = venv.EnvBuilder(with_pip=True)
builder.create(str(venv_path))

print(f"✅ Виртуальное окружение создано: {venv_path}")
print()
print("Активируйте окружение:")
print("  .venv\\Scripts\\activate.bat")
print()
print("Затем установите зависимости:")
print("  pip install -r requirements.txt")
print("  pip install -r requirements-dev.txt")




