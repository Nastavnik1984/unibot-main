# Установка Python 3.11

## Способ 1: Официальный установщик (рекомендуется)

### Шаг 1: Скачать Python 3.11
1. Откройте https://www.python.org/downloads/release/python-31111/
2. Прокрутите вниз до раздела "Files"
3. Скачайте **Windows installer (64-bit)** для вашей системы

Или прямые ссылки:
- **Python 3.11.11 (последняя версия 3.11):**
  - 64-bit: https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe
  - 32-bit: https://www.python.org/ftp/python/3.11.11/python-3.11.11.exe

### Шаг 2: Установка
1. Запустите скачанный установщик
2. **ВАЖНО:** Отметьте галочку **"Add Python to PATH"** внизу окна установки
3. Выберите **"Install Now"** или **"Customize installation"**
4. Дождитесь завершения установки

### Шаг 3: Проверка
Откройте новую командную строку и выполните:
```bash
python3.11 --version
# или
py -3.11 --version
```

## Способ 2: Через Chocolatey (если установлен)

Если у вас установлен Chocolatey:
```bash
choco install python311
```

## Способ 3: Через pyenv-win (управление версиями)

### Установка pyenv-win:
```powershell
# Через PowerShell (от администратора)
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

### Установка Python 3.11 через pyenv:
```bash
pyenv install 3.11.11
pyenv local 3.11.11
```

## Способ 4: Портативная версия (без установки)

1. Скачайте портативную версию Python 3.11
2. Распакуйте в папку (например, `C:\Python311`)
3. Добавьте в PATH вручную или используйте полный путь

## После установки

### Создание виртуального окружения с Python 3.11:

**Если установлен Python 3.11:**
```bash
python3.11 -m venv .venv
```

**Или через py launcher:**
```bash
py -3.11 -m venv .venv
```

### Активация и установка зависимостей:
```bash
.venv\Scripts\activate.bat
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Проверка версии

После установки проверьте:
```bash
python3.11 --version
# Должно быть: Python 3.11.11
```

## Важно

- Python 3.11 и Python 3.13 могут сосуществовать на одной системе
- Используйте `python3.11` для явного указания версии
- Или `py -3.11` через Python Launcher
- Для проекта создайте виртуальное окружение с Python 3.11

