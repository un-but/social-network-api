"""Зависимость для проверки доступа к объектам."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable
from typing import Annotated, Any, Callable

from fastapi import Depends, HTTPException, status

from auth_test_task.api.dependencies._common import db_dep
from auth_test_task.api.dependencies.auth import optional_auth_dep
from auth_test_task.api.dependencies.objects import (
    comment_dep,
    post_dep,
    role_rule_dep,
    user_dep,
)
from auth_test_task.db.dal import RoleRuleDAL
from auth_test_task.db.models import CommentModel, PostModel, RoleRuleModel, UserModel
from auth_test_task.schemas import ACTION_TYPE, OBJECT_TYPE, RoleRuleGet

logger = logging.getLogger("auth_test_task")

# access_type = Callable[
#     [role_rule_dep | user_dep | post_dep | comment_dep, optional_auth_dep, db_dep],
#     Awaitable[UserModel | PostModel | CommentModel | RoleRuleModel],
# ]


def access_to_obj(
    object_type: OBJECT_TYPE,
    action: ACTION_TYPE,
) -> Any:
    def get_user_id(obj: PostModel | CommentModel) -> uuid.UUID:
        return obj.user.id

    match object_type:
        case "role_rules":
            obj_dep = role_rule_dep

            def get_user_id(obj: RoleRuleModel) -> None:
                return None
        case "users":
            obj_dep = user_dep

            def get_user_id(obj: UserModel) -> uuid.UUID:
                return obj.id
        case "posts":
            obj_dep = post_dep

            def get_user_id(obj: PostModel | CommentModel) -> uuid.UUID:
                return obj.user.id
        case "comments":
            obj_dep = comment_dep

            def get_user_id(obj: PostModel | CommentModel) -> uuid.UUID:
                return obj.user.id

    async def wrapper(
        obj: obj_dep,
        user: optional_auth_dep,
        db: db_dep,
    ) -> UserModel | PostModel | CommentModel | RoleRuleModel:
        rule = await RoleRuleDAL.get(
            RoleRuleGet(
                role=user.role,
                object_type=object_type,
                action=action,
            ),
            db,
        )

        if user and (user.id == get_user_id(obj) or rule.allowed):
            return obj

        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    return wrapper


access_dep = Annotated[Any, Depends(access_to_obj)]
