"""Модуль включающий в себя все схемы. Для доступа следует импортировать все из этого модуля."""

# pyright: reportUnusedImport=false
# ruff: noqa: F401, RUF100

from __future__ import annotations

from social_network_api.schemas._common import BaseSchema, NoContentSchema
from social_network_api.schemas._configuration import config
from social_network_api.schemas._variables import (
    ACTION_TYPE,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    OBJECT_TYPE,
    USER_INCLUDE_TYPE,
    USER_ROLE,
)
from social_network_api.schemas.auth import AuthResponse, AuthWithEmail, Cookies
from social_network_api.schemas.comment import (
    CommentBaseResponse,
    CommentChildPostResponse,
    CommentChildUserResponse,
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from social_network_api.schemas.post import (
    PostBaseResponse,
    PostChildResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
)
from social_network_api.schemas.role_rule import (
    RoleRuleGet,
    RoleRuleResponse,
    RoleRuleUpdate,
    RuleInfo,
)
from social_network_api.schemas.user import (
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
