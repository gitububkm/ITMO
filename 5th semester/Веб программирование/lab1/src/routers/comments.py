from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies.auth import (
    get_comment_with_permission,
    get_current_user,
    get_optional_current_user,
    UserContext,
)
from src.models.comment import Comment
from src.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from src.services.comment_service import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])


def get_comment_service(db: AsyncSession = Depends(get_db)) -> CommentService:
    return CommentService(db)


@router.post("/", response_model=CommentResponse, status_code=201)
async def create_comment(
    comment: CommentCreate,
    current_user: UserContext = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    comment.author_id = current_user.id
    return await service.create_comment(comment)


@router.get("/", response_model=List[CommentResponse])
async def get_comments(
    skip: int = 0,
    limit: int = 100,
    _current_user: UserContext | None = Depends(get_optional_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.get_comments(skip, limit)


@router.get("/news/{news_id}", response_model=List[CommentResponse])
async def get_comments_by_news(
    news_id: int,
    _current_user: UserContext | None = Depends(get_optional_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.get_comments_by_news(news_id)


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    _current_user: UserContext | None = Depends(get_optional_current_user),
    service: CommentService = Depends(get_comment_service),
):
    comment = await service.get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    comment: Comment = Depends(get_comment_with_permission),
    service: CommentService = Depends(get_comment_service),
):
    updated = await service.update_comment(comment.id, comment_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Comment not found")
    return updated


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment: Comment = Depends(get_comment_with_permission),
    service: CommentService = Depends(get_comment_service),
):
    deleted = await service.delete_comment(comment.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")

