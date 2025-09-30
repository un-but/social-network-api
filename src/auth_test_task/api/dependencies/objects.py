"""Зависимости объектов."""

from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException, Query, status

from auth_test_task.api.dependencies._common import db_dep
from auth_test_task.api.dependencies.auth import auth_dep
from auth_test_task.db.dal import CommentDAL, PostDAL, RoleRuleDAL, UserDAL
from auth_test_task.db.models import CommentModel, PostModel, RoleRuleModel, UserModel
from auth_test_task.schemas import RoleRuleGet

logger = logging.getLogger("auth_test_task")


async def access_comment(
    comment_id: uuid.UUID,
    db: db_dep,
) -> CommentModel:
    """Проверяет, что комментарий принадлежит пользователю."""
    try:
        return await CommentDAL.get_by_id(comment_id, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Комментарий не найден")


async def access_post(
    post_id: uuid.UUID,
    db: db_dep,
) -> PostModel:
    """Проверяет, что пост принадлежит пользователю."""
    try:
        return await PostDAL.get_by_id(post_id, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пост не найден")


async def access_role_rule(
    db: db_dep,
    role_rule_info: RoleRuleGet = Query(...),
) -> RoleRuleModel:
    """Проверяет, что пользователь может менять правило роли."""
    try:
        return await RoleRuleDAL.get(role_rule_info, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Правило роли не найдено")


async def access_user(
    user_id: uuid.UUID,
    db: db_dep,
) -> UserModel:
    """Проверяет, что пользователь может менять данные другого пользователя."""
    try:
        return await UserDAL.get_by_id(user_id, db)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")
