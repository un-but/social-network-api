"""Вспомогательные функции для регистрации и авторизации пользователей."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, Literal

import jwt
from fastapi import HTTPException, Response, status

from auth_test_task.db.dal import UserDAL
from auth_test_task.schemas import AuthResponse, Cookies, UserResponse, config

if TYPE_CHECKING:
    import uuid

    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession

    from auth_test_task.db.models import UserModel


async def generate_access_token(user_id: uuid.UUID) -> str:
    return jwt.encode(
        {
            "sub": str(user_id),
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(seconds=config.api.jwt_access_expire_seconds),
        },
        key=config.api.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )


async def generate_refresh_token(refresh_id: str) -> str:
    return jwt.encode(
        {
            "sub": refresh_id,
            "type": "refresh",
            "exp": datetime.now(UTC) + timedelta(days=config.api.jwt_refresh_expire_days),
        },
        key=config.api.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )


async def get_user_by_token(
    token: str,
    token_type: Literal["access", "refresh"],
    db: AsyncSession,
    rd: Redis,
) -> UserModel:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            config.api.jwt_secret.get_secret_value(),
            algorithms=["HS256"],
        )

        if token_type != payload.get("type"):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Токен не содержит необходимой информации",
            )

        match token_type:
            case "access":  # Здесь sub это user_id
                user_id = payload["sub"]
            case "refresh":  # Здесь sub это токен из redis
                user_id = await rd.get(f"refresh_token:{payload['sub']}")

                if user_id is None:
                    raise LookupError

        user = await UserDAL.get_by_id(user_id, db)

        if user.is_active:
            return user

        raise LookupError
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Некорректный {token_type} токен")
    except LookupError:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"К {token_type} токену привязан несуществующий пользователь",
        )


async def create_user_tokens(
    user_info: UserResponse,
    rd: Redis,
    response: Response,
) -> AuthResponse:
    refresh_id = secrets.token_urlsafe(32)
    await rd.set(
        f"refresh_token:{refresh_id}",
        str(user_info.id),
        ex=config.api.jwt_refresh_expire_days * 3600 * 24,
    )

    access_token = await generate_access_token(user_info.id)
    refresh_token = await generate_refresh_token(refresh_id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=datetime.now(UTC) + timedelta(seconds=config.api.jwt_access_expire_seconds),
        httponly=True,
        secure=True,
        samesite="none",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=datetime.now(UTC) + timedelta(days=config.api.jwt_refresh_expire_days),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_info,
    )


async def delete_user_tokens(
    cookies: Cookies,
    rd: Redis,
    response: Response,
) -> None:
    try:
        payload: dict[str, Any] = jwt.decode(
            cookies.refresh_token,
            config.api.jwt_secret.get_secret_value(),
            algorithms=["HS256"],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Токен не содержит необходимой информации",
            )

        await rd.delete(f"refresh_token:{payload['sub']}")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Некорректный refresh токен")
    except LookupError:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "К refresh токену привязан несуществующий пользователь",
        )
    else:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
