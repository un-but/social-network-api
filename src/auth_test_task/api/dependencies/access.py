"""Зависимость для проверки доступа к объектам."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Annotated, Literal, TypeVar, overload

from fastapi import Depends, HTTPException, status

from auth_test_task.api.dependencies._common import db_dep
from auth_test_task.api.dependencies.auth import optional_auth_dep
from auth_test_task.api.dependencies.objects import get_comment, get_post, get_role_rule, get_user
from auth_test_task.db.dal import RoleRuleDAL
from auth_test_task.db.models import CommentModel, PostModel, RoleRuleModel, UserModel
from auth_test_task.schemas import ACTION_TYPE, OBJECT_TYPE, RoleRuleGet

logger = logging.getLogger("auth_test_task")

obj_type = TypeVar("obj_type", UserModel, PostModel, CommentModel, RoleRuleModel, None)


@overload
def access(
    object_type: Literal["users"],
    action: Literal["read", "update", "delete"],
) -> Callable[[UserModel, optional_auth_dep, db_dep], Awaitable[UserModel]]: ...


@overload
def access(
    object_type: Literal["posts"],
    action: Literal["read", "update", "delete"],
) -> Callable[[PostModel, optional_auth_dep, db_dep], Awaitable[PostModel]]: ...


@overload
def access(
    object_type: Literal["comments"],
    action: Literal["read", "update", "delete"],
) -> Callable[[CommentModel, optional_auth_dep, db_dep], Awaitable[CommentModel]]: ...


@overload
def access(
    object_type: Literal["role_rules"],
    action: Literal["read", "update", "delete"],
) -> Callable[[RoleRuleModel, optional_auth_dep, db_dep], Awaitable[RoleRuleModel]]: ...


@overload
def access(
    object_type: OBJECT_TYPE,
    action: Literal["create"],
) -> Callable[[None, optional_auth_dep, db_dep], Awaitable[None]]: ...


def access(
    object_type: OBJECT_TYPE,
    action: ACTION_TYPE,
) -> Callable[
    [obj_type, optional_auth_dep, db_dep],
    Awaitable[UserModel | PostModel | CommentModel | RoleRuleModel | None],
]:
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
    ) -> UserModel | PostModel | CommentModel | RoleRuleModel | None:
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

        if rule.allowed:
            return None

        if obj is not None and user and user.id == obj.get_user_id():
            return obj

        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    return wrapper
