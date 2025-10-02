"""Схемы для работы с правилами ролей пользователя."""

from __future__ import annotations

from auth_test_task.schemas._common import BaseSchema
from auth_test_task.schemas._variables import ACTION_TYPE, OBJECT_TYPE, USER_ROLE


class RoleRuleBase(BaseSchema):
    """Базовая схема правила роли пользователя."""

    role: USER_ROLE
    object_type: OBJECT_TYPE
    action: ACTION_TYPE


class RoleRuleGet(RoleRuleBase):
    """Схема получения правила роли пользователя."""


class RoleRuleCreate(RoleRuleBase):
    """Схема создания правила роли пользователя."""

    full_access: bool
    allowed: bool


class RoleRuleResponse(RoleRuleCreate):
    """Схема ответа с информацией о правиле роли пользователя."""


class RoleRuleUpdate(BaseSchema):
    """Схема обновления правила роли пользователя."""

    role: USER_ROLE | None = None
    object_type: OBJECT_TYPE | None = None
    action: ACTION_TYPE | None = None
    full_access: bool | None = None

    allowed: bool | None = None


class RoleRuleDelete(RoleRuleGet):
    """Схема удаления правила роли пользователя."""
