"""Модуль для работы с пользователями в базе данных."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from auth_test_task.db.models import UserModel

if TYPE_CHECKING:
    import uuid
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

    from auth_test_task.schemas import USER_INCLUDE_TYPE, UserCreate, UserUpdate


class UserDAL:
    """Класс для работы с пользователями в базе данных."""

    @staticmethod
    async def create(user_info: UserCreate, session: AsyncSession) -> UserModel:
        user = UserModel(**user_info.model_dump(by_alias=True))

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def get_by_id(
        user_id: uuid.UUID,
        session: AsyncSession,
        include: tuple[USER_INCLUDE_TYPE, ...] = (),
    ) -> UserModel:
        if user := await session.scalar(
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(
                *(selectinload(getattr(UserModel, include_attr)) for include_attr in include),
            ),
        ):
            return user

        msg = "Указанный пользователь не найден"
        raise LookupError(msg)

    @staticmethod
    async def get_with_email(
        email: str,
        session: AsyncSession,
        include: tuple[USER_INCLUDE_TYPE, ...] = (),
    ) -> UserModel:
        if user := await session.scalar(
            select(UserModel)
            .where(UserModel.email == email)
            .options(
                *(selectinload(getattr(UserModel, include_attr)) for include_attr in include),
            ),
        ):
            return user

        msg = "Указанный пользователь не найден"
        raise LookupError(msg)

    @staticmethod
    async def get_all(
        session: AsyncSession,
        include: tuple[USER_INCLUDE_TYPE, ...] = (),
    ) -> Sequence[UserModel]:
        users = await session.scalars(
            select(UserModel).options(
                *(selectinload(getattr(UserModel, include_attr)) for include_attr in include),
            ),
        )
        return users.all()

    @staticmethod
    async def update(
        user_id: uuid.UUID,
        update_info: UserUpdate,
        session: AsyncSession,
    ) -> UserModel:
        user = await UserDAL.get_by_id(user_id, session)

        for field, value in update_info.model_dump(exclude_none=True).items():
            setattr(user, field, value)

        await session.commit()
        return user

    @staticmethod
    async def deactivate(user_id: uuid.UUID, session: AsyncSession) -> None:
        user = await UserDAL.get_by_id(user_id, session)

        user.is_active = False
        await session.commit()

    @staticmethod
    async def drop(user_id: uuid.UUID, session: AsyncSession) -> None:
        user = await UserDAL.get_by_id(user_id, session)

        await session.delete(user)
        await session.commit()
