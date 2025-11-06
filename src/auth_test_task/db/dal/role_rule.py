"""Модуль для работы с правилами ролей пользователей в базе данных."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from sqlalchemy import select

from auth_test_task.db.models import RoleRuleModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from auth_test_task.schemas import RoleRuleCreate, RoleRuleDelete, RoleRuleGet, RoleRuleUpdate


class RoleRuleDAL:
    """Класс для работы с правилами ролей пользователей в базе данных."""

    @staticmethod
    async def create(role_rule_info: RoleRuleCreate, session: AsyncSession) -> RoleRuleModel:
        role_rule = RoleRuleModel(**role_rule_info.model_dump())

        session.add(role_rule)
        await session.commit()
        await session.refresh(role_rule)

        return role_rule

    @staticmethod
    async def get(
        role_rule_info: RoleRuleGet,
        session: AsyncSession,
    ) -> RoleRuleModel:
        if role_rule := await session.scalar(
            select(RoleRuleModel).where(
                (RoleRuleModel.role == role_rule_info.role)
                & (RoleRuleModel.object_type == role_rule_info.object_type)
                & (RoleRuleModel.action == role_rule_info.action)
                & (RoleRuleModel.owned == role_rule_info.owned)
            )  # TODO автоматизировать чтобы не требовалось указывать первичные ключи напрямую
        ):
            return role_rule

        msg = "Указанное правило роли не найден"
        raise LookupError(msg)

    @staticmethod
    async def get_all(
        session: AsyncSession,
    ) -> Sequence[RoleRuleModel]:
        role_rules = await session.scalars(select(RoleRuleModel))
        return role_rules.all()

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

    @staticmethod
    async def drop(role_rule_info: RoleRuleDelete, session: AsyncSession) -> None:
        role_rule = await RoleRuleDAL.get(role_rule_info, session)

        await session.delete(role_rule)
        await session.commit()
