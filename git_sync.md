# Синхронизация с GitHub

Репозиторий: `https://github.com/Nastavnik1984/unibot-main.git`  
Ветка: `main` → `origin/main`

## Если не синхронизируется (push не идёт)

### 1. Проверить статус в терминале

Открой терминал **в папке проекта** и выполни:

```powershell
cd "c:\Users\Евгений\Documents\unibot-main"
git status
git remote -v
```

Убедись, что видишь `origin` и ветку `main`.

### 2. Сначала подтянуть изменения с GitHub (pull)

```powershell
git pull origin main
```

Если попросит логин/пароль — см. пункт 4.

### 3. Отправить свои коммиты (push)

```powershell
git push origin main
```

Если ошибка **Authentication failed** или **403** — нужна авторизация (п. 4).  
Если ошибка **rejected** — кто-то уже пушил в `main`, сделай снова `git pull origin main`, затем `git push origin main`.

### 4. Авторизация на GitHub (HTTPS)

GitHub больше не принимает обычный пароль при push. Нужен **Personal Access Token (PAT)**:

1. Зайди на GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**.
2. **Generate new token (classic)**.
3. Отметь право **repo**.
4. Скопируй токен (один раз показывают).
5. При следующем `git push` или `git pull` введи:
   - **Username:** твой логин GitHub (Nastavnik1984).
   - **Password:** вставь **токен** (не пароль от аккаунта).

Windows может сохранить учётные данные в диспетчере учётых записей — тогда вводить нужно один раз.

### 5. Если в Cursor/VS Code не синхронизируется

Интерфейс «Sync» в Cursor делает pull + push. Если там ошибка:

- Открой **Output** → выбери **Git** и посмотри текст ошибки.
- Выполни `git push origin main` и `git pull origin main` вручную в терминале (см. выше) — так часто видно точную причину.

### 6. Проверить, что remote и ветка правильные

```powershell
git remote -v
git branch -vv
```

Должно быть: `origin` → `https://github.com/Nastavnik1984/unibot-main.git`, ветка `main` отслеживает `origin/main`.







