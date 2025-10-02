"""Модели SQLAlchemy ORM."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import override

import bcrypt
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
    validates,
)

from auth_test_task.schemas import (
    ACTION_TYPE,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    OBJECT_TYPE,
    USER_ROLE,
)

rename_pattern = re.compile(r"(?<!^)(?=[A-Z])")


class BaseModel(DeclarativeBase):
    """Базовый класс для моделей SQLAlchemy.

    Автоматически генерирует имя таблицы в snake_case во множественном числе.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Генерирует имя таблицы из имени класса."""
        class_name = re.sub(
            rename_pattern,
            "_",
            cls.__name__.replace("Model", ""),
        ).lower()
        return class_name + "s" if class_name[-1] != "y" else class_name[:-1] + "ies"

    # abstract method
    def get_user_id(self) -> uuid.UUID | None:
        msg = "Необходимо реализовать метод get_user_id в дочернем классе."
        raise NotImplementedError(msg)


class UserModel(BaseModel):
    """Модель пользователя (в т.ч. и администратора)."""

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)

    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[USER_ROLE] = mapped_column(default="user")

    name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    email: Mapped[str] = mapped_column(String(255), unique=True)
    _password: Mapped[str] = mapped_column(
        "password",
        String(255),
    )

    posts: Mapped[list[PostModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    comments: Mapped[list[CommentModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    @validates("_password")
    def validate_and_hash_password(self, key: str, value: str) -> str:
        if not value or len(value) < MIN_PASSWORD_LENGTH or len(value) > MAX_PASSWORD_LENGTH:
            msg = "Password must be at least 8 characters long and at most 64 characters long."
            raise ValueError(msg)

        return bcrypt.hashpw(value.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(raw_password.encode("utf-8"), self._password.encode("utf-8"))

    @override
    def get_user_id(self) -> uuid.UUID | None:
        return self.id


class PostModel(BaseModel):
    """Модель поста."""

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    content: Mapped[str] = mapped_column(String(1000))

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(back_populates="posts", lazy="joined")

    comments: Mapped[list[CommentModel]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    @override
    def get_user_id(self) -> uuid.UUID | None:
        return self.user.id


class CommentModel(BaseModel):
    """Модель комментария."""

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    content: Mapped[str] = mapped_column(String(500))

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(back_populates="comments", lazy="joined")

    post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("posts.id"))
    post: Mapped[PostModel] = relationship(back_populates="comments", lazy="joined")

    @override
    def get_user_id(self) -> uuid.UUID | None:
        return self.user.id


class RoleRuleModel(BaseModel):
    """Правила доступа для ролей и объектов."""

    role: Mapped[USER_ROLE] = mapped_column(primary_key=True)
    object_type: Mapped[OBJECT_TYPE] = mapped_column(primary_key=True)
    action: Mapped[ACTION_TYPE] = mapped_column(primary_key=True)
    full_access: Mapped[bool] = mapped_column(default=False)

    allowed: Mapped[bool] = mapped_column()

    @override
    def get_user_id(self) -> uuid.UUID | None:
        return None
