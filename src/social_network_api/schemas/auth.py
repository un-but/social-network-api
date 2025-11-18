"""Схемы для аутентификации, авторизации и разлогинивания пользователя."""

from __future__ import annotations

from pydantic import EmailStr, Field

from social_network_api.schemas._common import BaseSchema
from social_network_api.schemas.user import UserResponse


class Cookies(BaseSchema):
    """Схема для кук с токенами."""

    access_token: str | None = None
    refresh_token: str | None = None


class AuthWithEmail(BaseSchema):
    """Схема для создания пользователя."""

    email: EmailStr
    password: str = Field(alias="_password", min_length=8, max_length=64)


class AuthResponse(BaseSchema):
    """Схема для ответа с токенами и данными пользователя."""

    access_token: str
    refresh_token: str
    user: UserResponse
