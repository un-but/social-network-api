"""Эндпоинты, отвечающие за управление комментариями."""

import logging
from optparse import check_choice
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from auth_test_task.api.dependencies import auth_dep, comment_dep, db_dep, detect_rule, post_dep
from auth_test_task.db.dal import CommentDAL
from auth_test_task.schemas import CommentCreate, CommentResponse, CommentUpdate, RuleInfo
from auth_test_task.utils.access import check_rule, choose_rule

logger = logging.getLogger("auth_test_task")
router = APIRouter(
    prefix="/comments",
    tags=["Управление комментариями"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Комментарий не найден"},
    },
)


@router.post(
    "/",
    summary="Создать комментарий",
    response_description="Информация о комментарие: комментарий успешно создан",
)
async def create_comment(
    comment_info: CommentCreate,
    post: post_dep,
    authorized_user: auth_dep,
    create_rule_info: Annotated[RuleInfo, detect_rule("comments", "create")],
    getting_rule_info: Annotated[RuleInfo, detect_rule("comments", "read")],
    db: db_dep,
) -> CommentResponse:
    check_rule(create_rule_info.owned_rule)

    try:
        comment = await CommentDAL.create(authorized_user.id, post.id, comment_info, db)
    except IntegrityError:
        logger.exception("Нарушение ограничений данных при создании комментария")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        check_rule(choose_rule(comment, authorized_user, getting_rule_info))
        return CommentResponse.model_validate(comment)


@router.get(
    "/",
    summary="Получить все комментарии",
    response_description="Информация о комментариях: список успешно сформирован",
)
async def get_all_comments(
    authorized_user: auth_dep,
    rule_info: Annotated[RuleInfo, detect_rule("comments", "read")],
    db: db_dep,
) -> list[CommentResponse]:
    check_rule(rule_info.alien_rule)  # TODO(UnBut) сделать запрос данных в зависимости от правил
    comments = await CommentDAL.get_all(db)

    return [CommentResponse.model_validate(comment) for comment in comments]


@router.get(
    "/{comment_id}",
    summary="Получить комментарий",
    response_description="Информация о комментарие: комментарий успешно найден",
)
async def get_comment(
    comment: comment_dep,
    authorized_user: auth_dep,
    rule_info: Annotated[RuleInfo, detect_rule("comments", "read")],
) -> CommentResponse:
    check_rule(choose_rule(comment, authorized_user, rule_info))

    return CommentResponse.model_validate(comment)


@router.patch(
    "/{comment_id}",
    summary="Обновить комментарий",
    response_description="Информация о комментарие: комментарий успешно обновлён",
)
async def update_comment(
    update_info: CommentUpdate,
    comment: comment_dep,
    db: db_dep,
    authorized_user: auth_dep,
    update_rule_info: Annotated[RuleInfo, detect_rule("comments", "update")],
    getting_rule_info: Annotated[RuleInfo, detect_rule("comments", "read")],
) -> CommentResponse:
    check_rule(choose_rule(comment, authorized_user, update_rule_info))

    try:
        comment = await CommentDAL.update(comment.id, update_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        check_rule(choose_rule(comment, authorized_user, getting_rule_info))
        return CommentResponse.model_validate(comment)


@router.delete(
    "/{comment_id}",
    summary="Удалить комментарий",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Пустой ответ: комментарий успешно удалён",
)
async def delete_comment(
    comment: comment_dep,
    db: db_dep,
    authorized_user: auth_dep,
    rule_info: Annotated[RuleInfo, detect_rule("comments", "delete")],
) -> Response:
    check_rule(choose_rule(comment, authorized_user, rule_info))

    try:
        await CommentDAL.drop(comment.id, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
