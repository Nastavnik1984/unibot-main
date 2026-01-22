"""Прямое создание виртуального окружения."""
import subprocess
import sys
import shutil
from pathlib import Path

project_root = Path(__file__).parent
venv_path = project_root / ".venv"

print("=" * 60)
print("  СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ")
print("=" * 60)
print()

# Удаляем старое окружение
if venv_path.exists():
    print("Удаление старого окружения...")
    shutil.rmtree(venv_path)
    print("✅ Удалено")

# Пробуем найти Python 3.11
python_commands = [
    (["py", "-3.11"], "py -3.11"),
    (["python3.11"], "python3.11"),
    (["python"], "python (текущий)"),
]

python_found = None
python_cmd = None

print("Поиск Python 3.11...")
for cmd, desc in python_commands:
    try:
        result = subprocess.run(
            cmd + ["--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"Найден: {desc} -> {version}")
            if "3.11" in version:
                python_cmd = cmd
                python_found = True
                print(f"✅ Используем: {desc}")
                break
            elif cmd[0] == "python" and "3.13" in version:
                print(f"⚠️  Найден Python 3.13 (не 3.11), но можно использовать")
                python_cmd = cmd
                python_found = False
    except:
        continue

if not python_cmd:
    print("❌ Python не найден!")
    sys.exit(1)

# Создаём виртуальное окружение
print()
print("Создание виртуального окружения...")
try:
    subprocess.run(
        python_cmd + ["-m", "venv", str(venv_path)],
        cwd=project_root,
        check=True
    )
    print("✅ Виртуальное окружение создано")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)

# Проверяем
python_exe = venv_path / "Scripts" / "python.exe"
if python_exe.exists():
    result = subprocess.run([str(python_exe), "--version"], capture_output=True, text=True)
    print(f"✅ Проверка: {result.stdout.strip()}")
else:
    print("❌ python.exe не найден")
    sys.exit(1)

print()
print("=" * 60)
print("  ✅ ГОТОВО!")
print("=" * 60)
print()
print("Активируйте окружение:")
print("  .venv\\Scripts\\activate.bat")
print()
print("Затем установите зависимости:")
print("  pip install -r requirements.txt")
print("  pip install -r requirements-dev.txt")




