"""Схемы для работы с пользователями."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import AliasChoices, EmailStr, Field

from auth_test_task.schemas._common import BaseSchema
from auth_test_task.schemas._variables import USER_ROLE

if TYPE_CHECKING:  # Требуется для корректной работы отложенного импорта
    from auth_test_task.schemas import CommentChildUserResponse, PostChildResponse


class UserBase(BaseSchema):
    """Базовая схема пользователя."""

    name: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(max_length=255)


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    role: USER_ROLE = "user"
    password: str = Field(
        validation_alias=AliasChoices("password", "_password"),
        serialization_alias="_password",
        min_length=8,
        max_length=64,
    )


class UserResponse(UserBase):
    """Схема для ответа с данными пользователя."""

    id: uuid.UUID

    created_at: datetime

    posts: list[PostChildResponse] | None = None
    comments: list[CommentChildUserResponse] | None = None

    _deferred = ("posts", "comments")


class UserFullResponse(UserResponse):
    """Схема для ответа со всеми данными пользователя."""

    is_active: bool = Field(exclude=True)
    role: USER_ROLE


class UserUpdate(BaseSchema):
    """Схема для обновления данных пользователя."""

    name: str | None = Field(default=None, min_length=2, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(
        default=None,
        serialization_alias="_password",
        min_length=8,
        max_length=64,
    )

    role: USER_ROLE | None = None
    is_active: bool | None = None
