"""Зависимость для проверки доступа к объектам."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated, Any, Literal, TypeVar, overload

from fastapi import Depends, HTTPException, status

from auth_test_task.api.dependencies._common import db_dep
from auth_test_task.api.dependencies.auth import optional_auth_dep
from auth_test_task.api.dependencies.objects import (
    access_comment,
    access_post,
    access_role_rule,
    access_user,
)
from auth_test_task.db.dal import RoleRuleDAL
from auth_test_task.db.models import CommentModel, PostModel, RoleRuleModel, UserModel
from auth_test_task.schemas import ACTION_TYPE, OBJECT_TYPE, RoleRuleGet

logger = logging.getLogger("auth_test_task")

obj_type = TypeVar("obj_type", UserModel, PostModel, CommentModel, RoleRuleModel)


@overload
def access_to_obj(
    object_type: Literal["users"],
    action: ACTION_TYPE,
) -> Callable[[UserModel, optional_auth_dep, db_dep], Awaitable[UserModel]]: ...


@overload
def access_to_obj(
    object_type: Literal["posts"],
    action: ACTION_TYPE,
) -> Callable[[PostModel, optional_auth_dep, db_dep], Awaitable[PostModel]]: ...


@overload
def access_to_obj(
    object_type: Literal["comments"],
    action: ACTION_TYPE,
) -> Callable[[CommentModel, optional_auth_dep, db_dep], Awaitable[CommentModel]]: ...


@overload
def access_to_obj(
    object_type: Literal["role_rules"],
    action: ACTION_TYPE,
) -> Callable[[RoleRuleModel, optional_auth_dep, db_dep], Awaitable[RoleRuleModel]]: ...


def access_to_obj(
    object_type: OBJECT_TYPE,
    action: ACTION_TYPE,
) -> Callable[
    [obj_type, optional_auth_dep, db_dep],
    Awaitable[UserModel | PostModel | CommentModel | RoleRuleModel],
]:
    match object_type:
        case "role_rules":
            obj_func = access_role_rule
        case "users":
            obj_func = access_user
        case "posts":
            obj_func = access_post
        case "comments":
            obj_func = access_comment

    async def wrapper(
        obj: Annotated[obj_type, Depends(obj_func)],
        user: optional_auth_dep,
        db: db_dep,
    ) -> UserModel | PostModel | CommentModel | RoleRuleModel:
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

        if user and user.id == obj.get_user_id():
            return obj

        if rule.allowed:
            return obj

        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    return wrapper
