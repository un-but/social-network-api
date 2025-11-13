"""Вспомогательные функции для проверки доступа."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException, status

from auth_test_task.db.dal import RoleRuleDAL
from auth_test_task.schemas import RoleRuleGet, RuleInfo

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from auth_test_task.db.models import BaseModel, UserModel
    from auth_test_task.schemas import ACTION_TYPE, OBJECT_TYPE, BaseSchema


async def get_rule(
    authorized_user: UserModel,
    object_type: OBJECT_TYPE,
    action: ACTION_TYPE,
    db: AsyncSession,
) -> RuleInfo:
    try:
        rule_info = RuleInfo(
            *[
                await RoleRuleDAL.get(
                    RoleRuleGet(
                        role=authorized_user.role,
                        object_type=object_type,
                        action=action,
                        owned=owned,
                    ),
                    db,
                )
                for owned in (True, False)
            ]
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Правило не найдено")
    else:
        return rule_info


def check_access(user: UserModel | None, obj: BaseModel, rule: RuleInfo) -> bool:
    return (
        user and user.get_user_id() == obj.get_user_id() and rule.owned_rule.allowed
    ) or rule.alien_rule.allowed


def validate_to_necessary_schema[TFull: BaseSchema, TPartial: BaseSchema](
    obj: BaseModel,
    authorized_user: UserModel,
    rule: RuleInfo,
    full_schema: type[TFull],
    partial_schema: type[TPartial],
) -> TFull | TPartial:
    suitable_rule = (
        rule.owned_rule if authorized_user.get_user_id() == obj.get_user_id() else rule.alien_rule
    )

    if not suitable_rule.allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")

    return (full_schema if suitable_rule.full_access else partial_schema).model_validate(obj)


def validate_to_schema[T: BaseSchema](
    obj: BaseModel,
    authorized_user: UserModel,
    rule: RuleInfo,
    schema: type[T],
) -> T:
    suitable_rule = (
        rule.owned_rule if authorized_user.get_user_id() == obj.get_user_id() else rule.alien_rule
    )

    if not suitable_rule.allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")

    return schema.model_validate(obj)
