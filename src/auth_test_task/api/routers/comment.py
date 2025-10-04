"""Эндпоинты, отвечающие за управление комментариями."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from auth_test_task.api.dependencies import auth_dep, comment_dep, db_dep, detect_rule, post_dep
from auth_test_task.db.dal import CommentDAL
from auth_test_task.db.models import RoleRuleModel
from auth_test_task.schemas import CommentCreate, CommentResponse, CommentUpdate

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
    user: auth_dep,
    _: Annotated[RoleRuleModel, detect_rule("comments", "create")],
    db: db_dep,
) -> CommentResponse:
    try:
        comment = await CommentDAL.create(user.id, post.id, comment_info, db)
    except IntegrityError:
        logger.exception("Нарушение ограничений данных при создании комментария")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return CommentResponse.model_validate(comment)


@router.get(
    "/{comment_id}",
    summary="Получить комментарий",
    response_description="Информация о комментарие: комментарий успешно найден",
)
async def get_comment(
    comment: comment_dep,
    authorized_user: auth_dep,
    rule: Annotated[RoleRuleModel, detect_rule("comments", "read", check_allowed=False)],
) -> CommentResponse:
    if not rule.allowed and authorized_user.get_user_id() != comment.get_user_id():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    return CommentResponse.model_validate(comment)


# @router.get(
#     "/",
#     summary="Получить все комментарии",
#     response_description="Информация о комментариях: список успешно сформирован",
# )
# async def get_all_comments(
#     db: db_dep,
# ) -> list[CommentResponse]:
#     comments = await CommentDAL.get_all(db)
#
#     return [CommentResponse.model_validate(comment) for comment in comments]


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
    rule: Annotated[RoleRuleModel, detect_rule("comments", "update", check_allowed=False)],
) -> CommentResponse:
    if not rule.allowed and authorized_user.get_user_id() != comment.get_user_id():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    try:
        comment = await CommentDAL.update(comment.id, update_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
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
    rule: Annotated[RoleRuleModel, detect_rule("comments", "delete", check_allowed=False)],
) -> Response:
    if not rule.allowed and authorized_user.get_user_id() != comment.get_user_id():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    try:
        await CommentDAL.drop(comment.id, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
