"""Зависимости для FastAPI приложения."""

# pyright: reportUnusedImport=false
# ruff: noqa: F401, RUF100

from __future__ import annotations

from auth_test_task.api.dependencies._common import cookies_dep, db_dep, rd_dep
from auth_test_task.api.dependencies.access import access
from auth_test_task.api.dependencies.auth import auth_dep, optional_auth_dep
from auth_test_task.api.dependencies.objects import (
    comment_dep,
    post_dep,
    role_rule_dep,
    user_dep,
)
