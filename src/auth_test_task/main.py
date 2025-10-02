"""Модуль для запуска API.

Для корректной работы требуются правильно настроенные файлы config.toml и .env.
Данные о полях в них можно найти в файле src/auth_test_task/schemas/_configuration.py.
"""

from __future__ import annotations

from fastapi import FastAPI, status

from auth_test_task.api.routers import auth, comment, post, role_rule, users
from auth_test_task.schemas import config

app = FastAPI(
    title=config.api.name,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Нарушение ограничений полей в базе данных"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Необходима авторизация"},
        status.HTTP_403_FORBIDDEN: {"description": "Доступ запрещён"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Ошибка валидации данных в запросе"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Ошибка сервера, пожалуйста сообщите разработчикам"
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Сервис временно недоступен, пожалуйста сообщите разработчикам"
        },
    },
)

app.include_router(auth.router)

app.include_router(users.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(role_rule.router)
