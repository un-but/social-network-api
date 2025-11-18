"""Модуль для работы с моделями ORM. Рекомендую импортировать напрямую из этого модуля модели."""

# pyright: reportUnusedImport=false
# ruff: noqa: F401, RUF100

from __future__ import annotations

from social_network_api.db.dal.comment import CommentDAL
from social_network_api.db.dal.post import PostDAL
from social_network_api.db.dal.role_rule import RoleRuleDAL
from social_network_api.db.dal.user import UserDAL
