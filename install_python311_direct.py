
"""Прямая установка Python 3.11."""
import urllib.request
import subprocess
import sys
import os
from pathlib import Path

print("=" * 60)
print("  АВТОМАТИЧЕСКАЯ УСТАНОВКА PYTHON 3.11")
print("=" * 60)
print()

# URL для скачивания Python 3.11 (последняя стабильная версия)
# Пробуем несколько возможных версий
python_versions = [
    "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe",  # Последняя стабильная
    "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe",
    "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe",
]

python_url = python_versions[0]  # Используем первую (самую новую)
temp_dir = Path(os.environ.get("TEMP", "C:\\Temp"))
installer_path = temp_dir / "python-3.11.9-amd64.exe"

# Шаг 1: Скачивание
print("[1/3] Скачивание установщика Python 3.11...")
print("Пробую скачать доступную версию Python 3.11...")
print("Это может занять несколько минут...")
print()

# Пробуем скачать разные версии, если одна не работает
downloaded = False
last_error = None

for version_url in python_versions:
    try:
        version_name = version_url.split("/")[-2]  # Извлекаем версию из URL
        installer_path = temp_dir / f"python-{version_name}-amd64.exe"
        
        print(f"Пробую скачать Python {version_name}...")
        
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, (downloaded * 100) // total_size) if total_size > 0 else 0
            print(f"\rСкачано: {percent}%", end="", flush=True)
        
        urllib.request.urlretrieve(version_url, installer_path, show_progress)
        print()
        print(f"✅ Установщик скачан: {installer_path}")
        downloaded = True
        python_url = version_url
        break
    except Exception as e:
        last_error = e
        print(f"\n⚠️  Не удалось скачать {version_name}, пробую следующую версию...")
        continue

if not downloaded:
    print(f"\n❌ Ошибка скачивания всех версий. Последняя ошибка: {last_error}")
    print()
    print("Скачайте Python 3.11 вручную:")
    print("1. Откройте: https://www.python.org/downloads/")
    print("2. Выберите Python 3.11.x")
    print("3. Скачайте Windows installer (64-bit)")
    print()
    print("Или попробуйте прямые ссылки:")
    for url in python_versions:
        print(f"   {url}")
    input("\nНажмите Enter для выхода...")
    sys.exit(1)

print()
print("[2/3] Запуск установщика...")
print()
print("⚠️  ВАЖНО: В открывшемся окне установки:")
print("   1. Отметьте 'Add Python to PATH' внизу окна")
print("   2. Нажмите 'Install Now'")
print("   3. Дождитесь завершения установки")
print()
print("Запускаю установщик...")
print()

try:
    # Запуск установщика
    subprocess.Popen([str(installer_path)], shell=True)
    print("✅ Установщик запущен")
    print()
except Exception as e:
    print(f"❌ Ошибка запуска установщика: {e}")
    print()
    print("Запустите установщик вручную:")
    print(f"  {installer_path}")
    input("\nНажмите Enter для выхода...")
    sys.exit(1)

print("[3/3] Инструкции после установки:")
print()
print("После завершения установки:")
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
print()
input("Нажмите Enter для выхода...")
