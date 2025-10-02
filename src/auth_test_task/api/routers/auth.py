"""Эндпоинты, отвечающие за авторизацию пользователя."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from auth_test_task.api.dependencies import auth_dep, cookies_dep, db_dep, rd_dep
from auth_test_task.api.utils import (
    create_user_tokens,
    delete_user_tokens,
    get_user_by_token,
)
from auth_test_task.db.dal import UserDAL
from auth_test_task.schemas import AuthResponse, AuthWithEmail, UserResponse

logger = logging.getLogger("auth_test_task")
router = APIRouter(
    prefix="/auth",
    tags=["Авторизация"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
    },
)


@router.post(
    "/",
    summary="Авторизоваться в аккаунт",
    response_description="Токены и пользователь: авторизация успешно завершена",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Введён неверный email или пароль"},
        status.HTTP_403_FORBIDDEN: {
            "description": "Пользователь уже авторизован и не является администратором",
        },
    },
)
async def login(
    auth_info: AuthWithEmail,
    user: auth_dep,
    db: db_dep,
    rd: rd_dep,
    response: Response,
) -> AuthResponse:
    if user and user.role not in ("admin", "manager"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Вы уже авторизованы")

    try:
        user = await UserDAL.get_with_email(auth_info.email, db)

        if not user.is_active or not user.check_password(auth_info.password):
            raise LookupError
    except LookupError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный email или пароль")
    else:
        logger.info("User %s logged in by email %s", user.id, user.email)
        return await create_user_tokens(UserResponse.model_validate(user), rd, response)


@router.post(
    "/refresh",
    summary="Обновить токены по refresh токену",
    response_description="Токены и пользователь: обновление токенов успешно завершено",
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Введён несуществующий refresh токен"},
    },
)
async def refresh_access_token(
    cookies: cookies_dep,
    db: db_dep,
    rd: rd_dep,
    response: Response,
) -> AuthResponse:
    if cookies.refresh_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Необходима авторизация")

    if user := await get_user_by_token(cookies.refresh_token, "refresh", db, rd):
        await rd.delete(cookies.refresh_token)
        return await create_user_tokens(UserResponse.model_validate(user), rd, response)

    raise HTTPException(status.HTTP_403_FORBIDDEN, "Токен не найден")


@router.delete(
    "/",
    summary="Выйти из аккаунта",
    response_description="Пустой ответ: успешный выход из аккаунта",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    cookies: cookies_dep,
    response: Response,
    rd: rd_dep,
) -> Response:
    await delete_user_tokens(cookies, rd, response)
    response.status_code = status.HTTP_204_NO_CONTENT

    return response
