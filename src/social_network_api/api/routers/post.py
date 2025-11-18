"""Эндпоинты, отвечающие за управление постами."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from social_network_api.api.dependencies import auth_dep, db_dep, find_rule_info, post_dep
from social_network_api.db.dal import PostDAL
from social_network_api.schemas import PostCreate, PostResponse, PostUpdate, RuleInfo
from social_network_api.utils.access import check_rule, choose_rule

logger = logging.getLogger("social_network_api")
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
    authorized_user: auth_dep,
    create_rule_info: Annotated[RuleInfo, find_rule_info("posts", "create")],
    getting_rule_info: Annotated[RuleInfo, find_rule_info("posts", "read")],
    db: db_dep,
) -> PostResponse:
    check_rule(create_rule_info.owned_rule)

    try:
        post = await PostDAL.create(authorized_user.id, post_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        check_rule(choose_rule(post, authorized_user, getting_rule_info))
        return PostResponse.model_validate(post)


@router.get(
    "/",
    summary="Получить все посты",
    response_description="Информация о постах: список успешно сформирован",
)
async def get_all_posts(
    rule_info: Annotated[RuleInfo, find_rule_info("posts", "read")],
    db: db_dep,
) -> list[PostResponse]:
    check_rule(rule_info.alien_rule)
    posts = await PostDAL.get_all(db)

    return [PostResponse.model_validate(post) for post in posts]


@router.get(
    "/{post_id}",
    summary="Получить пост",
    response_description="Информация о посте: пост успешно найден",
)
async def get_post(
    post: post_dep,
    authorized_user: auth_dep,
    rule_info: Annotated[RuleInfo, find_rule_info("posts", "read")],
) -> PostResponse:
    check_rule(choose_rule(post, authorized_user, rule_info))

    return PostResponse.model_validate(post)


@router.patch(
    "/{post_id}",
    summary="Обновить пост",
    response_description="Информация о посте: пост успешно обновлён",
)
async def update_post(
    update_info: PostUpdate,
    post: post_dep,
    authorized_user: auth_dep,
    update_rule_info: Annotated[RuleInfo, find_rule_info("posts", "update")],
    getting_rule_info: Annotated[RuleInfo, find_rule_info("posts", "read")],
    db: db_dep,
) -> PostResponse:
    check_rule(choose_rule(post, authorized_user, update_rule_info))

    try:
        post = await PostDAL.update(post.id, update_info, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        check_rule(choose_rule(post, authorized_user, getting_rule_info))
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
    rule_info: Annotated[RuleInfo, find_rule_info("posts", "delete")],
    db: db_dep,
) -> Response:
    check_rule(choose_rule(post, authorized_user, rule_info))

    try:
        await PostDAL.drop(post.id, db)
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нарушение ограничений данных")
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
