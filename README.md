# Chat with model

Проект чат-клиента на React/Vite и API на FastAPI с PostgreSQL и SQLAlchemy.
Описание текущих API-ограничений и план для списка чатов находятся в
[Api.md](./Api.md).

## Схема базы данных

В приложении определены таблицы `users`, `models`, `sessions`, `messages`.
Таблица `generations` удалена.

```mermaid
erDiagram
    USERS {
        UUID id PK
        VARCHAR username UK
        VARCHAR email UK
        VARCHAR password
    }

    MODELS {
        UUID id PK
        TEXT provider
        TEXT display_name
        INTEGER context_window
        BOOLEAN supports_streaming
    }

    SESSIONS {
        UUID id PK
        UUID user_id FK "nullable"
        UUID model_id FK
        TEXT system_prompt "nullable"
        FLOAT temperature
        INTEGER max_tokens
        TEXT title "nullable"
        BOOLEAN is_archived
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    MESSAGES {
        UUID id PK
        UUID session_id FK
        ENUM role "system | user | assistant | tool"
        TEXT content
        INTEGER token_count "nullable"
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    USERS ||--o{ SESSIONS : "user_id"
    MODELS ||--o{ SESSIONS : "model_id"
    SESSIONS ||--o{ MESSAGES : "session_id, cascade delete"
```

ORM-связи доступны как `user.sessions` и `session.user`. `user_id` пока допускает
`NULL`; создание сессии ещё не связывает её с владельцем. Добавление колонки в
уже существующую таблицу требует миграции — `create_all()` не обновляет схему.

## Запуск фронтенда

```powershell
cd frontend
npm install
npm run dev
```

По умолчанию клиент обращается к API на `http://localhost:8000`. URL можно
переопределить переменной `VITE_API_URL`.

## Текущее состояние

Фронтенд содержит вход/регистрацию, настройки нового чата и интерфейс диалога.
Создание списка чатов, восстановление истории из списка, корректное владение
сессиями и некоторые контракты API ещё требуют реализации. Подробный перечень
и объявленные маршруты см. в [Api.md](./Api.md).
