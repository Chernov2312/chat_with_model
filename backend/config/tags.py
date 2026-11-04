from enum import StrEnum


class RouteTags(StrEnum):
    AUTH = "Авторизация"
    USERS = "Пользователи"
    LESSONS = "Уроки"
    PROGRESS = "Прогресс"
    SESSION = "Сессии"
    HEALTH_TEST = "Тест запуска бэка"
