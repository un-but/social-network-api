"""Эндпоинты, отвечающие за управление всеми пользователями."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError

from auth_test_task.api.dependencies import (
    access,
    auth_dep,
    db_dep,
    detect_rule,
    user_dep,
)
from auth_test_task.api.dependencies.objects import receive_user as gt_user
from auth_test_task.db.dal import UserDAL
from auth_test_task.db.models import RoleRuleModel, UserModel
from auth_test_task.schemas import (
    USER_INCLUDE_TYPE,
    UserCreate,
    UserFullResponse,
    UserResponse,
    UserUpdate,
)

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
)
async def create(
    user_info: UserCreate,
    db: db_dep,
    rule: Annotated[RoleRuleModel, detect_rule("users", "create")],
) -> UserResponse | UserFullResponse:
    try:
        user_info.role = user_info.role if rule.full_access else "user"
        user = await UserDAL.create(user_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return (UserFullResponse if rule.full_access else UserResponse).model_validate(user)


@router.get(
    "/me",
    summary="Получить своего пользователя",
    response_description="Информация о пользователе: пользователь успешно найден",
)
async def get_user(
    user: auth_dep,
    db: db_dep,
    rule: Annotated[RoleRuleModel, detect_rule("users", "read")],
    include: tuple[USER_INCLUDE_TYPE, ...] = Query(default=()),
) -> UserFullResponse | UserResponse:
    user = await UserDAL.get_by_id(user.id, db, include)
    return (UserFullResponse if rule.full_access else UserResponse).model_validate(user)


@router.get(
    "/{user_id}",
    summary="Получить любого пользователя",
    response_description="Информация о пользователе: пользователь успешно найден",
)
async def get_any_user(
    user: user_dep,
    authorized_user: auth_dep,
    rule: Annotated[RoleRuleModel, detect_rule("users", "read", check_allowed=False)],
    db: db_dep,
    include: tuple[USER_INCLUDE_TYPE, ...] = Query(default=()),
) -> UserResponse | UserFullResponse:
    if not rule.allowed and authorized_user.id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")

    user = await UserDAL.get_by_id(user.id, db, include)
    return (UserFullResponse if rule.full_access else UserResponse).model_validate(user)


# @router.get(
#     "/",
#     summary="Получить всех пользователей",
#     response_description="Информация о пользователях: список успешно сформирован",
# )
# async def get_all_users(
#     db: db_dep,
#     include: tuple[USER_INCLUDE_TYPE, ...] = Query(default=()),
# ) -> list[UserFullResponse | UserResponse]:
#     users = await UserDAL.get_all(db, include)
#
#     return [UserResponse.model_validate(user) for user in users]


@router.patch(
    "/{user_id}",
    summary="Обновить или удалить любого пользователя",
    response_description="Информация о пользователе: пользователь успешно обновлён/удалён",
)
async def update_user(
    update_info: UserUpdate,
    user: user_dep,
    authorized_user: auth_dep,
    rule: Annotated[RoleRuleModel, detect_rule("users", "read", check_allowed=False)],
    db: db_dep,
) -> UserResponse | UserFullResponse:
    if not rule.allowed and authorized_user.id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")

    try:
        user = await UserDAL.update(user.id, update_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return (UserFullResponse if rule.full_access else UserResponse).model_validate(user)


@router.delete(
    "/{user_id}",
    summary="Удалить любого пользователя вместе с данными",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Пустой ответ: пользователь успешно удалён",
)
async def hard_delete_any_user(
    user: user_dep,
    rule: Annotated[RoleRuleModel, detect_rule("users", "delete")],
    db: db_dep,
) -> Response:
    try:
        await UserDAL.drop(user.id, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
