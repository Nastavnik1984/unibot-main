"""Автоматическая установка Python 3.11."""
import subprocess
import sys
import urllib.request
import os
from pathlib import Path

print("=" * 60)
print("  АВТОМАТИЧЕСКАЯ УСТАНОВКА PYTHON 3.11")
print("=" * 60)
print()

# URL для скачивания Python 3.11.11
python_url = "https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe"
installer_path = Path(os.environ.get("TEMP", "C:\\Temp")) / "python-3.11.11-amd64.exe"

print("[1/3] Скачивание установщика Python 3.11.11...")
print(f"URL: {python_url}")
print(f"Путь: {installer_path}")
print("Это может занять несколько минут...")
print()

try:
    urllib.request.urlretrieve(python_url, installer_path)
    print(f"✅ Установщик скачан: {installer_path}")
except Exception as e:
    print(f"❌ Ошибка скачивания: {e}")
    print()
    print("Скачайте вручную:")
    print(python_url)
    sys.exit(1)

print()
print("[2/3] Запуск установщика...")
print()
print("⚠️  ВАЖНО: В открывшемся окне установки:")
print("   1. Отметьте 'Add Python to PATH' внизу окна")
print("   2. Нажмите 'Install Now'")
print("   3. Дождитесь завершения установки")
print()

# Запуск установщика
try:
    subprocess.Popen([str(installer_path)], shell=True)
    print("✅ Установщик запущен")
    print()
    print("Дождитесь завершения установки Python 3.11")
    print()
except Exception as e:
    print(f"❌ Ошибка запуска установщика: {e}")
    print()
    print("Запустите установщик вручную:")
    print(f"  {installer_path}")
    sys.exit(1)

print("[3/3] После установки:")
print()
print("1. Перезапустите командную строку")
print("2. Проверьте установку:")
print("   py -3.11 --version")
print()
print("3. Создайте виртуальное окружение с Python 3.11:")
print("   py -3.11 -m venv .venv")
print()
print("Или запустите скрипт:")
print("   recreate_venv_python311.bat")
print()
print("=" * 60)
print("  УСТАНОВКА ЗАПУЩЕНА")
print("=" * 60)

