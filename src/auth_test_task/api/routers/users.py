"""Эндпоинты, отвечающие за управление всеми пользователями."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError

from auth_test_task.api.dependencies import (
    auth_dep,
    db_dep,
    detect_rule,
    user_dep,
)
from auth_test_task.db.dal import UserDAL
from auth_test_task.schemas import (
    USER_INCLUDE_TYPE,
    RuleInfo,
    UserCreate,
    UserFullResponse,
    UserResponse,
    UserUpdate,
)
from auth_test_task.utils.access import check_rule, choose_rule

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
    create_rule_info: Annotated[RuleInfo, detect_rule("users", "create")],
    getting_rule_info: Annotated[RuleInfo, detect_rule("users", "read")],
) -> UserResponse | UserFullResponse:
    check_rule(create_rule_info.owned_rule)

    try:
        user = await UserDAL.create(user_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return (
            UserFullResponse
            if check_rule(choose_rule(user, user, getting_rule_info)).full_access
            else UserResponse
        ).model_validate(user)


@router.get(
    "/",
    summary="Получить всех пользователей",
    response_description="Информация о пользователе: пользователь успешно найден",
)
async def get_all_users(
    authorized_user: auth_dep,
    rule_info: Annotated[RuleInfo, detect_rule("users", "read")],
    db: db_dep,
    include: tuple[USER_INCLUDE_TYPE, ...] = Query(default=()),
) -> list[UserResponse | UserFullResponse]:
    check_rule(rule_info.alien_rule)  # TODO(UnBut) сделать запрос данных в зависимости от правил
    users = await UserDAL.get_all(db, include)

    return [
        (UserFullResponse if rule_info.alien_rule.full_access else UserResponse).model_validate(
            user
        )
        for user in users
    ]


@router.get(
    "/me",
    summary="Получить своего пользователя",
    response_description="Информация о пользователях: список успешно сформирован",
)
async def get_user(
    authorized_user: auth_dep,
    db: db_dep,
    rule_info: Annotated[RuleInfo, detect_rule("users", "read")],
    include: tuple[USER_INCLUDE_TYPE, ...] = Query(default=()),
) -> UserFullResponse | UserResponse:
    check_rule(rule_info.owned_rule)  # Используется owned_rule так как это всегда сам пользователь

    user = await UserDAL.get_by_id(authorized_user.id, db, include)
    return (UserFullResponse if rule_info.owned_rule.full_access else UserResponse).model_validate(
        user
    )


@router.get(
    "/{user_id}",
    summary="Получить любого пользователя",
    response_description="Информация о пользователе: пользователь успешно найден",
)
async def get_any_user(
    user: user_dep,
    authorized_user: auth_dep,
    rule_info: Annotated[RuleInfo, detect_rule("users", "read")],
    db: db_dep,
    include: tuple[USER_INCLUDE_TYPE, ...] = Query(default=()),
) -> UserResponse | UserFullResponse:
    check_rule(choose_rule(user, authorized_user, rule_info))

    user = await UserDAL.get_by_id(user.id, db, include)
    return (UserFullResponse if rule_info.owned_rule.full_access else UserResponse).model_validate(
        user
    )


@router.patch(
    "/{user_id}",
    summary="Обновить или удалить любого пользователя",
    response_description="Информация о пользователе: пользователь успешно обновлён/удалён",
)
async def update_user(
    update_info: UserUpdate,
    user: user_dep,
    authorized_user: auth_dep,
    update_rule_info: Annotated[RuleInfo, detect_rule("users", "update")],
    getting_rule_info: Annotated[RuleInfo, detect_rule("users", "read")],
    db: db_dep,
) -> UserResponse | UserFullResponse:
    check_rule(choose_rule(user, authorized_user, update_rule_info))

    try:
        user = await UserDAL.update(user.id, update_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        suitable_rule = choose_rule(user, authorized_user, getting_rule_info)
        check_rule(suitable_rule)

        return (UserFullResponse if suitable_rule.full_access else UserResponse).model_validate(
            user
        )


@router.delete(
    "/{user_id}",
    summary="Удалить любого пользователя безопасно или вместе с данными",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Пустой ответ: пользователь успешно удалён",
)
async def delete_any_user(
    user: user_dep,
    authorized_user: auth_dep,
    db: db_dep,
    rule_info: Annotated[RuleInfo, detect_rule("users", "delete")],
    hard_delete: bool = Query(default=False),
) -> Response:
    check_rule(choose_rule(user, authorized_user, rule_info))

    try:
        if hard_delete:
            await UserDAL.drop(user.id, db)
        else:
            await UserDAL.deactivate(user.id, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
