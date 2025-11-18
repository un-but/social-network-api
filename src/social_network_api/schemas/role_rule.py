"""Схемы для работы с правилами ролей пользователя."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from social_network_api.schemas._common import BaseSchema
from social_network_api.schemas._variables import ACTION_TYPE, OBJECT_TYPE, USER_ROLE

if TYPE_CHECKING:
    from social_network_api.db.models import RoleRuleModel

# Схемы для создания и удаления отсутствуют, так как не предустматриваются после запуска приложения


class RoleRuleBase(BaseSchema):
    """Базовая схема правила роли пользователя."""

    role: USER_ROLE
    object_type: OBJECT_TYPE
    action: ACTION_TYPE
    owned: bool


class RoleRuleGet(RoleRuleBase):
    """Схема получения правила роли пользователя."""


class RoleRuleResponse(RoleRuleBase):
    """Схема ответа с информацией о правиле роли пользователя."""

    allowed: bool
    full_access: bool


class RoleRuleUpdate(BaseSchema):
    """Схема обновления правила роли пользователя."""

    allowed: bool | None = None
    full_access: bool | None = None


@dataclass
class RuleInfo:
    """Класс данных, включающих в себя правила для своих и чужих объектов."""

    owned_rule: RoleRuleModel
    alien_rule: RoleRuleModel
