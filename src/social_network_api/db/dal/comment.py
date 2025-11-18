"""Модуль для работы с комментариями в базе данных."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import TYPE_CHECKING

from sqlalchemy import select

from social_network_api.db.models import CommentModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from social_network_api.schemas import CommentCreate, CommentUpdate


class CommentDAL:
    """Класс для работы с комментариями в базе данных."""

    @staticmethod
    async def create(
        user_id: uuid.UUID,
        post_id: uuid.UUID,
        comment_info: CommentCreate,
        session: AsyncSession,
    ) -> CommentModel:
        comment = CommentModel(user_id=user_id, post_id=post_id, **comment_info.model_dump())

        session.add(comment)
        await session.commit()
        await session.refresh(comment)

        return comment

    @staticmethod
    async def get_by_id(
        comment_id: uuid.UUID,
        session: AsyncSession,
    ) -> CommentModel:
        if comment := await session.scalar(
            select(CommentModel).where(CommentModel.id == comment_id)
        ):
            return comment

        msg = "Указанный комментарий не найден"
        raise LookupError(msg)

    @staticmethod
    async def get_all(
        session: AsyncSession,
    ) -> Sequence[CommentModel]:
        comments = await session.scalars(select(CommentModel))
        return comments.unique().all()

    @staticmethod
    async def update(
        comment_id: uuid.UUID,
        update_info: CommentUpdate,
        session: AsyncSession,
    ) -> CommentModel:
        comment = await CommentDAL.get_by_id(comment_id, session)

        for field, value in update_info.model_dump(exclude_none=True).items():
            setattr(comment, field, value)

        await session.commit()
        return comment

    @staticmethod
    async def drop(comment_id: uuid.UUID, session: AsyncSession) -> None:
        comment = await CommentDAL.get_by_id(comment_id, session)

        await session.delete(comment)
        await session.commit()
