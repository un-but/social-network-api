"""Модуль для работы с правилами ролей пользователей в базе данных."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from sqlalchemy import and_, select
from sqlalchemy.inspection import inspect

from auth_test_task.db.models import RoleRuleModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from auth_test_task.schemas import RoleRuleGet, RoleRuleUpdate


class RoleRuleDAL:
    """Класс для работы с правилами ролей пользователей в базе данных."""

    @staticmethod
    async def get(
        role_rule_info: RoleRuleGet,
        session: AsyncSession,
    ) -> RoleRuleModel:
        # Важно чтобы первичные ключи были и в модели SQLAlchemy, и в схеме Pydantic
        primary_key_names = [field.key for field in inspect(RoleRuleModel).primary_key if field.key]

        if role_rule := await session.scalar(
            select(RoleRuleModel).where(
                and_(
                    *[
                        getattr(RoleRuleModel, name) == getattr(role_rule_info, name)
                        for name in primary_key_names
                    ]  # pyright: ignore[reportAny]
                )
            )
        ):
            return role_rule

        msg = "Указанное правило роли не найден"
        raise LookupError(msg)

    @staticmethod
    async def get_all(
        session: AsyncSession,
    ) -> Sequence[RoleRuleModel]:
        role_rules = await session.scalars(select(RoleRuleModel))
        return role_rules.unique().all()

    @staticmethod
    async def update(
        role_rule_info: RoleRuleGet,
        update_info: RoleRuleUpdate,
        session: AsyncSession,
    ) -> RoleRuleModel:
        role_rule = await RoleRuleDAL.get(role_rule_info, session)

        for field, value in update_info.model_dump(exclude_none=True).items():
            setattr(role_rule, field, value)

        await session.commit()
        return role_rule
