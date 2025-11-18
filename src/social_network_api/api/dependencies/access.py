"""Зависимость для проверки доступа к объектам."""

from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, status

from social_network_api.api.dependencies._common import db_dep
from social_network_api.api.dependencies.auth import optional_auth_dep
from social_network_api.schemas import ACTION_TYPE, OBJECT_TYPE, RuleInfo
from social_network_api.utils.access import get_rule_info

logger = logging.getLogger("social_network_api")


def find_rule_info(
    object_type: OBJECT_TYPE,
    action: ACTION_TYPE,
) -> RuleInfo:
    async def wrapper(
        authorized_user: optional_auth_dep,
        db: db_dep,
    ) -> RuleInfo:
        if not authorized_user:  # TODO(UnBut): #1 добавить роль guest
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Необходима авторизация")

        return await get_rule_info(authorized_user, object_type, action, db)

    return Depends(wrapper)  # pyright: ignore[reportAny]
