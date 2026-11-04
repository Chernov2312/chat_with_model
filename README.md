# TodoList || PetProject
[![linter_test](https://github.com/Chernov2312/ToDoList/actions/workflows/ci_linter_test.yml/badge.svg)](https://github.com/Chernov2312/ToDoList/actions/workflows/ci_linter_test.yml)
---

### Предварительные требования

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/downloads)

### Установка и запуск

1. Клонирование репозитория

```bash
git clone 
```

2. Переход в папку проекта

```bash
cd ToDoList
```

3. Настройка переменных окружения

Linux/macOS

```bash
cp .env.example .env
```

Windows (PowerShell)

```powershell
Copy-Item .env.example .env
```

4. Запуск проекта
```bash
docker-compose up --build
```

---
После запуска сервер будет доступен по адресу:

- Сайт: http://127.0.0.1:8000/


---

#### Функционал

**1. Пользователь проходит регистрацию**

Пользователь регистрируется в системе.

**2. Задания**

Пользователь может указывать сразу несколько заданий разной сложности, указывать им сроки выполнения

**3. История заданий**

После завершения результат сохраняется в историю пользователя. Для каждого задания доступны:
- дата и время
- выполнено/просрочено

---

#### Установка зависимостей

Для разработки

```bash
pip install -r requirements/dev.txt
```

Для запуска тестов

```bash
pip install -r requirements/test.txt
```

---

#### Запуск тестов

Проверка flake8

```bash
flake8
```

Проверка black

```bash
black --check .
```

Тесты PyTest
```bash
python3 manage.py test
```

---

###### Разработчик

```
Максим Чернов
```

---

<small>© 2026 Work by Max</small>