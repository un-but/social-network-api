"""Модуль включающий в себя все схемы. Для доступа следует импортировать все из этого модуля."""

# pyright: reportUnusedImport=false
# ruff: noqa: F401, RUF100

from __future__ import annotations

from auth_test_task.schemas._common import BaseSchema, NoContentSchema
from auth_test_task.schemas._configuration import config
from auth_test_task.schemas._variables import (
    ACTION_TYPE,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    OBJECT_TYPE,
    USER_INCLUDE_TYPE,
    USER_ROLE,
)
from auth_test_task.schemas.auth import AuthResponse, AuthWithEmail, Cookies
from auth_test_task.schemas.comment import (
    CommentBaseResponse,
    CommentChildPostResponse,
    CommentChildUserResponse,
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from auth_test_task.schemas.post import (
    PostBaseResponse,
    PostChildResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
)
from auth_test_task.schemas.role_rule import (
    RoleRuleGet,
    RoleRuleResponse,
    RoleRuleUpdate,
    RuleInfo,
)
from auth_test_task.schemas.user import (
    UserCreate,
    UserFullResponse,
    UserResponse,
    UserUpdate,
)

UserResponse.model_rebuild()
UserFullResponse.model_rebuild()
PostResponse.model_rebuild()

CommentChildPostResponse.model_rebuild()
CommentChildUserResponse.model_rebuild()
CommentResponse.model_rebuild()
