"""Схемы для работы с комментариями."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from social_network_api.schemas._common import BaseSchema

if TYPE_CHECKING:  # Требуется для корректной работы отложенного импорта
    from social_network_api.schemas import PostChildResponse, UserResponse


class CommentCreate(BaseSchema):
    """Схема для создания комментария."""

    content: str = Field(min_length=1, max_length=500)


class CommentBaseResponse(CommentCreate):
    """Базовая схема для ответа с комментарием."""

    id: uuid.UUID
    created_at: datetime


class CommentChildPostResponse(CommentBaseResponse):
    """Схема для ответа с комментарием в составе поста."""

    user: UserResponse | None = None


class CommentChildUserResponse(CommentBaseResponse):
    """Схема для ответа с комментарием в составе пользователя."""

    post: PostChildResponse | None = None


class CommentResponse(CommentChildUserResponse, CommentChildPostResponse):
    """Схема для ответа с комментарием."""


class CommentUpdate(BaseSchema):
    """Схема для обновления комментария."""

    content: str | None = Field(default=None, min_length=1, max_length=500)
