"""Зависимости авторизации."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status

from social_network_api.api.dependencies._common import cookies_dep, db_dep, rd_dep
from social_network_api.db.models import UserModel
from social_network_api.utils.auth import get_user_by_token

logger = logging.getLogger("social_network_api")


async def authorize_user(
    cookies: cookies_dep,
    db: db_dep,
    rd: rd_dep,
) -> UserModel:
    """Авторизует пользователя по токену из куки."""
    if cookies.access_token:
        return await get_user_by_token(cookies.access_token, "access", db, rd)

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Необходима авторизация")


auth_dep = Annotated[UserModel, Depends(authorize_user)]


async def optional_authorize_user(
    cookies: cookies_dep,
    db: db_dep,
    rd: rd_dep,
) -> UserModel | None:
    """Может авторизовать пользователя, если передан токен."""
    if cookies.access_token:
        return await authorize_user(cookies, db, rd)
    return None


optional_auth_dep = Annotated[UserModel | None, Depends(optional_authorize_user)]
