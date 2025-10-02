"""Зависимость для проверки доступа к объектам."""

from __future__ import annotations

import logging
from typing import Annotated, TypeVar

from fastapi import Depends, HTTPException, status
from fastapi.params import Depends as DependsParam

from auth_test_task.api.dependencies._common import db_dep
from auth_test_task.api.dependencies.auth import optional_auth_dep
from auth_test_task.api.dependencies.objects import get_comment, get_post, get_role_rule, get_user
from auth_test_task.db.dal import RoleRuleDAL
from auth_test_task.db.models import CommentModel, PostModel, UserModel
from auth_test_task.schemas import ACTION_TYPE, OBJECT_TYPE, RoleRuleGet

logger = logging.getLogger("auth_test_task")

obj_type = TypeVar("obj_type", UserModel, PostModel, CommentModel, None)


def access(
    object_type: OBJECT_TYPE,
    action: ACTION_TYPE,
) -> DependsParam:
    match object_type:
        case "role_rules":
            obj_func = get_role_rule
        case "users":
            obj_func = get_user
        case "posts":
            obj_func = get_post
        case "comments":
            obj_func = get_comment

    if action == "create":
        obj_func = None

    async def wrapper(
        obj: Annotated[obj_type, Depends(obj_func)],
        user: optional_auth_dep,
        db: db_dep,
    ) -> None:
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Необходима авторизация")

        rule = await RoleRuleDAL.get(
            RoleRuleGet(
                role=user.role,
                object_type=object_type,
                action=action,
            ),
            db,
        )

        if rule.allowed or (obj is not None and user and user.id == obj.get_user_id()):
            return

        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    return Depends(wrapper)  # pyright: ignore[reportAny]
