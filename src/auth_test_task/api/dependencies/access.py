"""Зависимость для проверки доступа к объектам."""

from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, status

from auth_test_task.api.dependencies._common import db_dep
from auth_test_task.api.dependencies.auth import optional_auth_dep
from auth_test_task.db.dal import RoleRuleDAL
from auth_test_task.db.models import RoleRuleModel
from auth_test_task.schemas import ACTION_TYPE, OBJECT_TYPE, RoleRuleGet

logger = logging.getLogger("auth_test_task")


def detect_rule(
    object_type: OBJECT_TYPE,
    action: ACTION_TYPE,
    check_allowed: bool = True,
) -> RoleRuleModel:
    async def wrapper(
        user: optional_auth_dep,
        db: db_dep,
    ) -> RoleRuleModel:
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Необходима авторизация")

        try:
            rule = await RoleRuleDAL.get(
                RoleRuleGet(
                    role=user.role,
                    object_type=object_type,
                    action=action,
                ),
                db,
            )
        except LookupError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Правило не найдено")
        else:
            if check_allowed and not rule.allowed:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")

            return rule

    return Depends(wrapper)  # pyright: ignore[reportAny]
