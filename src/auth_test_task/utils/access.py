"""Вспомогательные функции для проверки доступа."""

from __future__ import annotations

from typing import TYPE_CHECKING

from auth_test_task.schemas import RuleInfo

if TYPE_CHECKING:
    from auth_test_task.db.models import BaseModel, UserModel


def check_access(user: UserModel | None, obj: BaseModel, rule: RuleInfo) -> bool:
    return (
        user and user.get_user_id() == obj.get_user_id() and rule.owned_rule.allowed
    ) or rule.alien_rule.allowed
