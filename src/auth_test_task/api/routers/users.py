"""Эндпоинты, отвечающие за управление всеми пользователями."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError

from auth_test_task.api.dependencies import access, auth_dep, db_dep, user_dep
from auth_test_task.db.dal import UserDAL
from auth_test_task.db.dal.role_rule import RoleRuleDAL
from auth_test_task.db.models import RoleRuleModel
from auth_test_task.schemas import (
    USER_INCLUDE_TYPE,
    UserCreate,
    UserFullResponse,
    UserResponse,
    UserUpdate,
)
from auth_test_task.schemas.role_rule import RoleRuleGet

logger = logging.getLogger("auth_test_task")
router = APIRouter(
    prefix="/users",
    tags=["Управление пользователями"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
    },
)


@router.post(
    "/",
    summary="Создать пользователя",
    response_description="Информация о пользователе: пользователь успешно создан",
    dependencies=[access("users", "create", True)],
)
async def create(
    user_info: UserCreate,
    rule: Annotated[RoleRuleModel, access("users", "create", True)],
    db: db_dep,
) -> UserResponse:
    try:
        user_info.role = user_info.role if rule.full_access else "user"
        user = await UserDAL.create(user_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return UserResponse.model_validate(user)


@router.get(
    "/me",
    summary="Получить своего пользователя",
    response_description="Информация о пользователе: пользователь успешно найден",
)
async def get_user(
    user: auth_dep,
    db: db_dep,
    include: tuple[USER_INCLUDE_TYPE, ...] = Query(default=()),
) -> UserFullResponse | UserResponse:
    user = await UserDAL.get_by_id(user.id, db, include)
    rule = await RoleRuleDAL.get(
        RoleRuleGet(
            role=user.role,
            object_type="users",
            action="read",
        ),
        db,
    )

    return (UserFullResponse if rule.full_access else UserResponse).model_validate(user)


@router.get(
    "/{user_id}",
    summary="Получить любого пользователя",
    response_description="Информация о пользователе: пользователь успешно найден",
    dependencies=[access("users", "read")],
)
async def get_any_user(
    user: user_dep,
    db: db_dep,
    rule: Annotated[RoleRuleModel, access("users", "read", True)],
    include: tuple[USER_INCLUDE_TYPE, ...] = Query(default=()),
) -> UserResponse | UserFullResponse:
    user = await UserDAL.get_by_id(user.id, db, include)

    return (UserFullResponse if rule.full_access else UserResponse).model_validate(user)


@router.get(
    "/",
    summary="Получить всех пользователей",
    response_description="Информация о пользователях: список успешно сформирован",
)
async def get_all_users(
    db: db_dep,
    include: tuple[USER_INCLUDE_TYPE, ...] = Query(default=()),
) -> list[UserFullResponse | UserResponse]:
    users = await UserDAL.get_all(db, include)

    return [UserResponse.model_validate(user) for user in users]


@router.patch(
    "/{user_id}",
    summary="Обновить или удалить любого пользователя",
    response_description="Информация о пользователе: пользователь успешно обновлён/удалён",
    dependencies=[access("users", "update")],
)
async def update_any_user_with_role(
    update_info: UserUpdate,
    rule: Annotated[RoleRuleModel, access("users", "update", True)],
    user: user_dep,
    db: db_dep,
) -> UserResponse | UserFullResponse:
    try:
        user = await UserDAL.update(user.id, update_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return (UserFullResponse if rule.full_access else UserResponse).model_validate(user)


@router.delete(
    "/{user_id}",
    summary="Удалить пользователя вместе с данными",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Пустой ответ: пользователь успешно удалён",
    dependencies=[access("users", "delete", True)],
)
async def hard_delete_any_user(
    user: user_dep,
    db: db_dep,
) -> Response:
    try:
        await UserDAL.drop(user.id, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
