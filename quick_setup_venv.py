"""Быстрое создание виртуального окружения."""
import subprocess
import sys
import shutil
from pathlib import Path

root = Path(__file__).parent
venv = root / ".venv"

print("Создание виртуального окружения...")

# Удаляем старое
if venv.exists():
    shutil.rmtree(venv)
    print("Старое окружение удалено")

# Пробуем Python 3.11, если нет - используем текущий
for cmd in [["py", "-3.11"], ["python3.11"], ["python"]]:
    try:
        r = subprocess.run(cmd + ["--version"], capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            if "3.11" in r.stdout or cmd[0] == "python":
                print(f"Используем: {' '.join(cmd)}")
                subprocess.run(cmd + ["-m", "venv", str(venv)], cwd=root, check=True)
                print("✅ Готово!")
                print(f"Активируйте: .venv\\Scripts\\activate.bat")
                sys.exit(0)
    except:
        continue

print("❌ Ошибка")
sys.exit(1)




