from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from src.services.comment_service import CommentService
from src.dependencies.auth import (
    get_current_user,
    get_comment_with_permission,
    get_optional_current_user
)
from src.models.user import User
from src.models.comment import Comment
from typing import List

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentResponse, status_code=201)
def create_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment.author_id = current_user.id
    db_comment = Comment(**comment.model_dump())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/", response_model=List[CommentResponse])
def get_comments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    return CommentService.get_comments(db, skip, limit)

@router.get("/news/{news_id}", response_model=List[CommentResponse])
def get_comments_by_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    return CommentService.get_comments_by_news(db, news_id)

@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    comment = CommentService.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_update: CommentUpdate,
    comment: Comment = Depends(get_comment_with_permission),
    db: Session = Depends(get_db)
):
    update_data = comment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment: Comment = Depends(get_comment_with_permission),
    db: Session = Depends(get_db)
):
    db.delete(comment)
    db.commit()

