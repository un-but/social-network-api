"""Эндпоинты, отвечающие за управление правилами ролей."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from auth_test_task.api.dependencies import db_dep, detect_rule, role_rule_dep
from auth_test_task.db.dal import RoleRuleDAL
from auth_test_task.schemas import RoleRuleGet, RoleRuleResponse, RoleRuleUpdate, RuleInfo
from auth_test_task.utils.access import check_access, validate_to_schema

logger = logging.getLogger("auth_test_task")
router = APIRouter(
    prefix="/role-rules",
    tags=["Управление правилами ролей"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Правило роли не найдено"},
    },
)


@router.get(
    "/{role}/{object_type}/{action}/{owned}",
    summary="Получить правило роли",
    response_description="Информация о правиле роли: правило роли успешно найдено",
)
async def get_role_rule(
    role_rule: role_rule_dep,
    rule: Annotated[RuleInfo, detect_rule("role_rules", "read")],
) -> RoleRuleResponse:
    if not check_access(None, role_rule, rule):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    return RoleRuleResponse.model_validate(role_rule)


@router.get(
    "/",
    summary="Получить все правила ролей",
    response_description="Информация о правилах ролей: список успешно сформирован",
)
async def get_all_role_rules(
    rule: Annotated[RuleInfo, detect_rule("users", "read")],
    db: db_dep,
) -> list[RoleRuleResponse]:
    if not rule.alien_rule.allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    role_rules = await RoleRuleDAL.get_all(db)
    return [RoleRuleResponse.model_validate(role_rule) for role_rule in role_rules]


@router.patch(
    "/{role}/{object_type}/{action}/{owned}",
    summary="Обновить правило роли",
    response_description="Информация о правиле роли: правило роли успешно обновлёно",
)
async def update_role_rule(
    update_info: RoleRuleUpdate,
    role_rule: role_rule_dep,
    rule: Annotated[RuleInfo, detect_rule("role_rules", "update")],
    db: db_dep,
) -> RoleRuleResponse:
    if not check_access(None, role_rule, rule):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    try:
        role_rule = await RoleRuleDAL.update(RoleRuleGet.model_validate(role_rule), update_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return RoleRuleResponse.model_validate(role_rule)
