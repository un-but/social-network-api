"""Модуль для работы с постами в базе данных."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import TYPE_CHECKING

from sqlalchemy import select

from auth_test_task.db.models import PostModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from auth_test_task.schemas import PostCreate, PostUpdate


class PostDAL:
    """Класс для работы с постами в базе данных."""

    @staticmethod
    async def create(user_id: uuid.UUID, post_info: PostCreate, session: AsyncSession) -> PostModel:
        post = PostModel(user_id=user_id, **post_info.model_dump())

        session.add(post)
        await session.commit()
        await session.refresh(post)

        return post

    @staticmethod
    async def get_by_id(
        post_id: uuid.UUID,
        session: AsyncSession,
    ) -> PostModel:
        if post := await session.scalar(select(PostModel).where(PostModel.id == post_id)):
            return post

        msg = "Указанный пост не найден"
        raise LookupError(msg)

    @staticmethod
    async def get_all(
        session: AsyncSession,
    ) -> Sequence[PostModel]:
        posts = await session.scalars(select(PostModel))
        return posts.unique().all()

    @staticmethod
    async def update(
        post_id: uuid.UUID,
        update_info: PostUpdate,
        session: AsyncSession,
    ) -> PostModel:
        post = await PostDAL.get_by_id(post_id, session)

        for field, value in update_info.model_dump(exclude_none=True).items():
            setattr(post, field, value)

        await session.commit()
        return post

    @staticmethod
    async def drop(post_id: uuid.UUID, session: AsyncSession) -> None:
        post = await PostDAL.get_by_id(post_id, session)

        await session.delete(post)
        await session.commit()
