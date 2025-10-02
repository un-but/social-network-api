"""Эндпоинты, отвечающие за управление постами."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from auth_test_task.api.dependencies import access, auth_dep, db_dep, post_dep
from auth_test_task.db.dal import PostDAL
from auth_test_task.db.models import PostModel
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
    dependencies=[access("posts", "create")],
)
async def create_post(
    post_info: PostCreate,
    user: auth_dep,
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
    dependencies=[access("posts", "read")],
)
async def get_post(
    post: post_dep,
) -> PostResponse:
    return PostResponse.model_validate(post)


@router.get(
    "/",
    summary="Получить все посты",
    response_description="Информация о постах: список успешно сформирован",
    dependencies=[access("posts", "read")],
)
async def get_all_posts(
    db: db_dep,
) -> list[PostResponse]:
    posts = await PostDAL.get_all(db)

    return [PostResponse.model_validate(post) for post in posts]


@router.patch(
    "/",
    summary="Обновить пост",
    response_description="Информация о посте: пост успешно обновлён",
    dependencies=[access("posts", "update")],
)
async def update_post(
    update_info: PostUpdate,
    post: post_dep,
    db: db_dep,
) -> PostResponse:
    try:
        post = await PostDAL.update(post.id, update_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return PostResponse.model_validate(post)


@router.delete(
    "/",
    summary="Удалить пост",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Пустой ответ: пост успешно удалён",
    dependencies=[access("posts", "delete")],
)
async def delete_post(
    post: post_dep,
    db: db_dep,
) -> Response:
    try:
        await PostDAL.drop(post.id, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
