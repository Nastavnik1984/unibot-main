"""Создание виртуального окружения с Python 3.11."""
import subprocess
import sys
import shutil
from pathlib import Path

print("=" * 60)
print("  СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ С PYTHON 3.11")
print("=" * 60)
print()

project_root = Path(__file__).parent
venv_path = project_root / ".venv"

# Проверка Python 3.11
print("[1/4] Проверка Python 3.11...")
python311_commands = [
    ["py", "-3.11", "--version"],
    ["python3.11", "--version"],
    ["python", "--version"],  # Проверим текущий Python
]

python311_found = False
python_cmd = None

for cmd in python311_commands:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_output = result.stdout.strip()
            print(f"✅ Найден: {' '.join(cmd)} -> {version_output}")
            
            # Проверяем, что это Python 3.11
            if "3.11" in version_output:
                python311_found = True
                python_cmd = cmd[0] if len(cmd) == 2 else cmd
                if cmd[0] == "py":
                    python_cmd = ["py", "-3.11"]
                elif cmd[0] == "python3.11":
                    python_cmd = ["python3.11"]
                else:
                    # Проверяем версию текущего Python
                    if "3.11" in version_output:
                        python_cmd = ["python"]
                    else:
                        print(f"⚠️  Найден Python, но не версия 3.11: {version_output}")
                        continue
                break
    except (FileNotFoundError, subprocess.TimeoutExpired):
        continue

if not python311_found:
    print("❌ Python 3.11 не найден!")
    print()
    print("Доступные варианты:")
    print("1. Установите Python 3.11 (запустите install_python311_direct.py)")
    print("2. Используйте Python 3.13 (уже установлен)")
    print()
    
    choice = input("Создать виртуальное окружение с Python 3.13? (y/n): ").lower()
    if choice == 'y':
        python_cmd = ["python"]
        print("✅ Будет использован Python 3.13")
    else:
        print("Установка отменена")
        sys.exit(1)

print()
print("[2/4] Удаление старого виртуального окружения (если есть)...")
if venv_path.exists():
    try:
        shutil.rmtree(venv_path)
        print("✅ Старое окружение удалено")
    except Exception as e:
        print(f"⚠️  Ошибка удаления: {e}")
        print("Продолжаю...")
else:
    print("✅ Старое окружение не найдено")

print()
print("[3/4] Создание нового виртуального окружения...")

# Создаём команду для создания venv
if isinstance(python_cmd, list):
    venv_cmd = python_cmd + ["-m", "venv", str(venv_path)]
else:
    venv_cmd = [python_cmd, "-m", "venv", str(venv_path)]

try:
    result = subprocess.run(
        venv_cmd,
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True
    )
    print("✅ Виртуальное окружение создано")
except subprocess.CalledProcessError as e:
    print(f"❌ Ошибка создания виртуального окружения: {e}")
    if e.stderr:
        print(f"Ошибка: {e.stderr}")
    sys.exit(1)

print()
print("[4/4] Проверка созданного окружения...")

# Проверяем, что окружение создано
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
            print(f"✅ Виртуальное окружение работает: {result.stdout.strip()}")
        else:
            print("⚠️  Виртуальное окружение создано, но проверка не прошла")
    except Exception as e:
        print(f"⚠️  Ошибка проверки: {e}")
else:
    print("❌ Файл python.exe не найден в виртуальном окружении")
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
print("Или запустите скрипт:")
print("   recreate_venv_python311.bat")
print()




