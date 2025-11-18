"""Вспомогательные функции для проверки доступа."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from fastapi import HTTPException, status

from social_network_api.db.dal import RoleRuleDAL
from social_network_api.db.models import RoleRuleModel
from social_network_api.schemas import RoleRuleGet, RuleInfo

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from social_network_api.db.models import BaseModel, UserModel
    from social_network_api.schemas import ACTION_TYPE, OBJECT_TYPE


async def get_rule_info(
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


@overload
def check_rule(
    rule: RoleRuleModel,
    require_full_access: bool = False,
    raise_err: Literal[True] = True,
) -> RoleRuleModel: ...


@overload
def check_rule(
    rule: RoleRuleModel,
    require_full_access: bool = False,
    raise_err: Literal[False] = False,
) -> RoleRuleModel | None: ...


def check_rule(
    rule: RoleRuleModel,
    require_full_access: bool = False,
    raise_err: bool = True,
) -> RoleRuleModel | None:
    if rule.allowed and (not require_full_access or rule.full_access):
        return rule

    if raise_err:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Доступ к операции {rule.action} запрещён")

    return None


def choose_rule(
    obj: BaseModel,
    authorized_user: UserModel,
    rule_info: RuleInfo,
) -> RoleRuleModel:
    return (
        rule_info.owned_rule
        if authorized_user and obj and authorized_user.get_user_id() == obj.get_user_id()
        else rule_info.alien_rule
    )
