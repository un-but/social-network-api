"""Эндпоинты, отвечающие за управление правилами ролей."""

import logging

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from auth_test_task.api.dependencies import access, db_dep, role_rule_dep
from auth_test_task.db.dal import RoleRuleDAL
from auth_test_task.schemas import (
    RoleRuleCreate,
    RoleRuleDelete,
    RoleRuleGet,
    RoleRuleResponse,
    RoleRuleUpdate,
)

logger = logging.getLogger("auth_test_task")
router = APIRouter(
    prefix="/role-rules",
    tags=["Управление правилами ролей"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Правило роли не найдено"},
    },
)


@router.post(
    "/",
    summary="Создать правило роли",
    response_description="Информация о правиле роли: правило роли успешно создано",
    dependencies=[access("role_rules", "create")],
)
async def create_role_rule(
    role_rule_info: RoleRuleCreate,
    db: db_dep,
) -> RoleRuleResponse:
    try:
        role_rule = await RoleRuleDAL.create(role_rule_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return RoleRuleResponse.model_validate(role_rule)


@router.get(
    "/{role}/{object_type}/{action}",
    summary="Получить правило роли",
    response_description="Информация о правиле роли: правило роли успешно найдено",
    dependencies=[access("role_rules", "read")],
)
async def get_role_rule(
    role_rule: role_rule_dep,
) -> RoleRuleResponse:
    return RoleRuleResponse.model_validate(role_rule)


@router.get(
    "/",
    summary="Получить все правила ролей",
    response_description="Информация о правилах ролей: список успешно сформирован",
)
async def get_all_role_rules(db: db_dep) -> list[RoleRuleResponse]:
    role_rules = await RoleRuleDAL.get_all(db)

    return [RoleRuleResponse.model_validate(role_rule) for role_rule in role_rules]


@router.patch(
    "/",
    summary="Обновить правило роли",
    response_description="Информация о правиле роли: правило роли успешно обновлёно",
    dependencies=[access("role_rules", "update")],
)
async def update_role_rule(
    update_info: RoleRuleUpdate,
    role_rule: role_rule_dep,
    db: db_dep,
) -> RoleRuleResponse:
    try:
        role_rule = await RoleRuleDAL.update(
            RoleRuleGet(
                role=role_rule.role,
                object_type=role_rule.object_type,
                action=role_rule.action,
            ),
            update_info,
            db,
        )
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return RoleRuleResponse.model_validate(role_rule)


@router.delete(
    "/",
    summary="Удалить правило роли",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Пустой ответ: правило роли успешно удалёно",
    dependencies=[access("role_rules", "delete")],
)
async def delete_role_rule(
    role_rule: role_rule_dep,
    db: db_dep,
) -> Response:
    try:
        await RoleRuleDAL.drop(
            RoleRuleDelete(
                role=role_rule.role,
                object_type=role_rule.object_type,
                action=role_rule.action,
            ),
            db,
        )
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
