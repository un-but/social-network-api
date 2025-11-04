"""Зависимость для проверки доступа к объектам."""

from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, status

from auth_test_task.api.dependencies._common import db_dep
from auth_test_task.api.dependencies.auth import optional_auth_dep
from auth_test_task.db.dal import RoleRuleDAL
from auth_test_task.schemas import ACTION_TYPE, OBJECT_TYPE, RoleRuleGet, RuleInfo
from auth_test_task.utils.access import get_rule

logger = logging.getLogger("auth_test_task")


def detect_rule(
    object_type: OBJECT_TYPE,
    action: ACTION_TYPE,
) -> RuleInfo:
    async def wrapper(
        authorized_user: optional_auth_dep,
        db: db_dep,
    ) -> RuleInfo:
        if not authorized_user:  # TODO добавить роль guest
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Необходима авторизация")

        return await get_rule(authorized_user, object_type, action, db)

    return Depends(wrapper)  # pyright: ignore[reportAny]
