"""Проверка версии Python."""
import sys

print("=" * 60)
print("  ИНФОРМАЦИЯ О PYTHON")
print("=" * 60)
print()
print(f"Версия Python: {sys.version}")
print(f"Версия (краткая): {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print(f"Путь к интерпретатору: {sys.executable}")
print()
print("=" * 60)

# Проверка соответствия требованиям проекта
print("\nПроверка требований проекта:")
print("Проект требует: Python >= 3.11")
if sys.version_info.major == 3 and sys.version_info.minor >= 11:
    print("✅ Ваша версия Python подходит для проекта!")
else:
    print("❌ Ваша версия Python не подходит для проекта!")
    print("   Установите Python 3.11 или новее")




