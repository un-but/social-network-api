"""Зависимости объектов."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Path, status

from auth_test_task.api.dependencies._common import db_dep
from auth_test_task.db.dal import CommentDAL, PostDAL, RoleRuleDAL, UserDAL
from auth_test_task.db.models import CommentModel, PostModel, RoleRuleModel, UserModel
from auth_test_task.schemas import RoleRuleGet

logger = logging.getLogger("auth_test_task")


async def receive_role_rule(
    db: db_dep,
    role_rule: RoleRuleGet = Path(...),
) -> RoleRuleModel:
    try:
        return await RoleRuleDAL.get(role_rule, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Правило роли не найдено")


role_rule_dep = Annotated[RoleRuleModel, Depends(receive_role_rule)]


async def receive_user(
    user_id: uuid.UUID,
    db: db_dep,
) -> UserModel:
    try:
        return await UserDAL.get_by_id(user_id, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")


user_dep = Annotated[UserModel, Depends(receive_user)]


async def receive_post(
    post_id: uuid.UUID,
    db: db_dep,
) -> PostModel:
    try:
        return await PostDAL.get_by_id(post_id, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пост не найден")


post_dep = Annotated[PostModel, Depends(receive_post)]


async def receive_comment(
    comment_id: uuid.UUID,
    db: db_dep,
) -> CommentModel:
    try:
        return await CommentDAL.get_by_id(comment_id, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Комментарий не найден")


comment_dep = Annotated[CommentModel, Depends(receive_comment)]
