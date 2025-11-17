"""Схемы для работы с постами."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from auth_test_task.schemas._common import BaseSchema

if TYPE_CHECKING:  # Требуется для корректной работы отложенного импорта
    from auth_test_task.schemas import CommentChildPostResponse, UserResponse


class PostCreate(BaseSchema):
    """Схема для создания поста."""

    content: str = Field(min_length=1, max_length=1000)


class PostBaseResponse(PostCreate):
    """Базовая схема для ответа с постом."""

    id: uuid.UUID
    created_at: datetime


class PostChildResponse(PostBaseResponse):
    """Схема для ответа в качестве дочернего объекта."""

    comments: list[CommentChildPostResponse] | None = None


class PostResponse(PostChildResponse):
    """Схема для ответа с постом."""

    user: UserResponse


class PostUpdate(BaseSchema):
    """Схема для обновления поста."""

    content: str | None = Field(default=None, min_length=1, max_length=1000)
