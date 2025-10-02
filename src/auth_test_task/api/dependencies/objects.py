"""Зависимости объектов."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Path, Query, status

from auth_test_task.api.dependencies._common import db_dep
from auth_test_task.db.dal import CommentDAL, PostDAL, RoleRuleDAL, UserDAL
from auth_test_task.db.models import CommentModel, PostModel, RoleRuleModel, UserModel
from auth_test_task.schemas import ACTION_TYPE, OBJECT_TYPE, USER_ROLE, RoleRuleGet

logger = logging.getLogger("auth_test_task")


async def get_role_rule(
    db: db_dep,
    role_rule: RoleRuleGet = Path(...),
    # role: USER_ROLE = Query(...),
    # object_type: OBJECT_TYPE = Query(...),
    # action: ACTION_TYPE = Query(...),
) -> RoleRuleModel:
    """Проверяет, что пользователь может менять правило роли."""
    try:
        return await RoleRuleDAL.get(role_rule, db)
        # return await RoleRuleDAL.get(
        #     RoleRuleGet(
        #         role=role,
        #         object_type=object_type,
        #         action=action,
        #     ),
        #     db,
        # )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Правило роли не найдено")


role_rule_dep = Annotated[RoleRuleModel, Depends(get_role_rule)]


async def get_user(
    user_id: uuid.UUID,
    db: db_dep,
) -> UserModel:
    """Проверяет, что пользователь может менять данные другого пользователя."""
    try:
        return await UserDAL.get_by_id(user_id, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")


user_dep = Annotated[UserModel, Depends(get_user)]


async def get_post(
    post_id: uuid.UUID,
    db: db_dep,
) -> PostModel:
    """Проверяет, что пост принадлежит пользователю."""
    try:
        return await PostDAL.get_by_id(post_id, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пост не найден")


post_dep = Annotated[PostModel, Depends(get_post)]


async def get_comment(
    comment_id: uuid.UUID,
    db: db_dep,
) -> CommentModel:
    """Проверяет, что комментарий принадлежит пользователю."""
    try:
        return await CommentDAL.get_by_id(comment_id, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Комментарий не найден")


comment_dep = Annotated[CommentModel, Depends(get_comment)]
