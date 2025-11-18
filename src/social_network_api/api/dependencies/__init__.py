"""Зависимости для FastAPI приложения."""

# pyright: reportUnusedImport=false
# ruff: noqa: F401, RUF100

from __future__ import annotations

from social_network_api.api.dependencies._common import cookies_dep, db_dep, rd_dep
from social_network_api.api.dependencies.access import find_rule_info
from social_network_api.api.dependencies.auth import auth_dep, optional_auth_dep
from social_network_api.api.dependencies.objects import comment_dep, post_dep, role_rule_dep, user_dep
