"""Схемы для работы с правилами ролей пользователя."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from auth_test_task.schemas._common import BaseSchema
from auth_test_task.schemas._variables import ACTION_TYPE, OBJECT_TYPE, USER_ROLE

if TYPE_CHECKING:
    from auth_test_task.db.models import RoleRuleModel


class RoleRuleBase(BaseSchema):
    """Базовая схема правила роли пользователя."""

    role: USER_ROLE
    object_type: OBJECT_TYPE
    action: ACTION_TYPE
    owned: bool


class RoleRuleGet(RoleRuleBase):
    """Схема получения правила роли пользователя."""


class RoleRuleCreate(RoleRuleBase):
    """Схема создания правила роли пользователя."""

    allowed: bool
    full_access: bool


class RoleRuleResponse(RoleRuleCreate):
    """Схема ответа с информацией о правиле роли пользователя."""


class RoleRuleUpdate(BaseSchema):
    """Схема обновления правила роли пользователя."""

    role: USER_ROLE | None = None
    object_type: OBJECT_TYPE | None = None
    action: ACTION_TYPE | None = None
    owned: bool | None = None

    allowed: bool | None = None
    full_access: bool | None = None


class RoleRuleDelete(RoleRuleGet):
    """Схема удаления правила роли пользователя."""


@dataclass
class RuleInfo:
    """Класс данных правила.

    Включает в себя правила для своих и чужих объектов
    """

    owned_rule: RoleRuleModel
    alien_rule: RoleRuleModel
