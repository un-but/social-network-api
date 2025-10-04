"""Эндпоинты, отвечающие за управление постами."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from auth_test_task.api.dependencies import auth_dep, db_dep, detect_rule, post_dep
from auth_test_task.db.dal import PostDAL
from auth_test_task.db.models import RoleRuleModel
from auth_test_task.schemas import PostCreate, PostResponse, PostUpdate

logger = logging.getLogger("auth_test_task")
router = APIRouter(
    prefix="/posts",
    tags=["Управление постами"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Пост не найден"},
    },
)


@router.post(
    "/",
    summary="Создать пост",
    response_description="Информация о посте: пост успешно создан",
)
async def create_post(
    post_info: PostCreate,
    user: auth_dep,
    _: Annotated[RoleRuleModel, detect_rule("posts", "create")],
    db: db_dep,
) -> PostResponse:
    try:
        post = await PostDAL.create(user.id, post_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return PostResponse.model_validate(post)


@router.get(
    "/{post_id}",
    summary="Получить пост",
    response_description="Информация о посте: пост успешно найден",
)
async def get_post(
    post: post_dep,
    authorized_user: auth_dep,
    rule: Annotated[RoleRuleModel, detect_rule("posts", "read", check_allowed=False)],
) -> PostResponse:
    if not rule.allowed and authorized_user.get_user_id() != post.get_user_id():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    return PostResponse.model_validate(post)


# @router.get(
#     "/",
#     summary="Получить все посты",
#     response_description="Информация о постах: список успешно сформирован",
# )
# async def get_all_posts(
#     db: db_dep,
# ) -> list[PostResponse]:
#     posts = await PostDAL.get_all(db)
#
#     return [PostResponse.model_validate(post) for post in posts]


@router.patch(
    "/{post_id}",
    summary="Обновить пост",
    response_description="Информация о посте: пост успешно обновлён",
)
async def update_post(
    update_info: PostUpdate,
    post: post_dep,
    authorized_user: auth_dep,
    rule: Annotated[RoleRuleModel, detect_rule("posts", "update", check_allowed=False)],
    db: db_dep,
) -> PostResponse:
    if not rule.allowed and authorized_user.get_user_id() != post.get_user_id():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    try:
        post = await PostDAL.update(post.id, update_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return PostResponse.model_validate(post)


@router.delete(
    "/{post_id}",
    summary="Удалить пост",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Пустой ответ: пост успешно удалён",
)
async def delete_post(
    post: post_dep,
    authorized_user: auth_dep,
    rule: Annotated[RoleRuleModel, detect_rule("posts", "delete", check_allowed=False)],
    db: db_dep,
) -> Response:
    if not rule.allowed and authorized_user.get_user_id() != post.get_user_id():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ запрещён")

    try:
        await PostDAL.drop(post.id, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
