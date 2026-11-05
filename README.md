# Chat with model

Веб-приложение для общения с GigaChat: frontend на React/Vite, API на FastAPI,
хранение пользователей, сессий и истории в PostgreSQL.

## Возможности

- Регистрация и вход с выдачей Bearer-токена.
- Создание и удаление чатов, просмотр списка своих сессий.
- Потоковая генерация ответа через Server-Sent Events.
- Сохранение и повторная загрузка истории сообщений.
- Системный промпт для сессии.
- Один настроенный провайдер и модель — GigaChat `GigaChat-3-Ultra`.
- Профиль пользователя и обновление email.

Выбор модели из каталога пока не реализован: новые сессии используют
`GigaChat-3-Ultra`. Документация API и текущие ограничения описаны в
[Api.md](./Api.md).

## Требования

- Docker Desktop с Docker Compose.
- Действующие GigaChat credentials для переменной `GIGA_KEY`.

## Запуск через Docker Compose

1. Создайте локальный `.env` на основе шаблона.

   PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Откройте `.env` и задайте свои значения:

   - `GIGA_KEY` — ключ авторизации GigaChat.
   - `CLIENT_ID` — Client ID, требуемый конфигурацией приложения.
   - `SECRET_KEY` — замените на случайный секрет для подписи токенов.
   - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — параметры локальной
     PostgreSQL.
   - `VITE_API_URL` оставьте `http://localhost:8000`, если не меняете порт API.

   Не публикуйте `.env` и не помещайте рабочие credentials в git.

3. Из корня репозитория запустите:

   ```powershell
   docker compose up --build
   ```

   Compose запустит PostgreSQL, дождётся его healthcheck, затем запустит API и
   frontend. При старте backend создаёт отсутствующие таблицы.

4. Откройте приложение:

   - Frontend: <http://localhost:5173>
   - API и OpenAPI Swagger UI: <http://localhost:8000/docs>
   - Проверка API: <http://localhost:8000/health>

Создайте аккаунт, войдите и нажмите **Новый чат**. Для браузерного доступа
backend разрешает CORS для `localhost:5173` и `127.0.0.1:5173`.

## Управление контейнерами

Остановить контейнеры, сохранив данные PostgreSQL:

```powershell
docker compose down
```

Снова запустить без пересборки:

```powershell
docker compose up
```

Для просмотра логов:

```powershell
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

PostgreSQL хранит данные в именованном томе `postgres_data`. Удаление тома
удалит локальную базу и все созданные в ней данные.

## Запуск frontend без Docker

Для локальной разработки frontend можно запустить отдельно, оставив API и
PostgreSQL в Docker:

```powershell
cd frontend
npm install
npm run dev
```

Адрес backend задаётся через `VITE_API_URL`; по умолчанию используется
`http://localhost:8000`.

## Настройки приложения

В корневом `.env` задаются PostgreSQL credentials, `SECRET_KEY`, срок жизни
access token, `GIGA_KEY`, `CLIENT_ID` и `VITE_API_URL`. В Compose для backend
`POSTGRES_HOST` автоматически переопределяется на hostname сервиса `postgres`.

Не добавляйте реальные ключи и пароли в `.env.example` или исходный код.
