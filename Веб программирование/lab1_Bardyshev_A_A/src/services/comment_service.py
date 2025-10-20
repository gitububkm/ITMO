from sqlalchemy.orm import Session
from src.models.comment import Comment
from src.schemas.comment import CommentCreate, CommentUpdate
from typing import List, Optional

class CommentService:
    @staticmethod
    def create_comment(db: Session, comment: CommentCreate) -> Comment:
        db_comment = Comment(**comment.model_dump())
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.id == comment_id).first()

    @staticmethod
    def get_comments(db: Session, skip: int = 0, limit: int = 100) -> List[Comment]:
        return db.query(Comment).offset(skip).limit(limit).all()

    @staticmethod
    def get_comments_by_news(db: Session, news_id: int) -> List[Comment]:
        return db.query(Comment).filter(Comment.news_id == news_id).all()

    @staticmethod
    def update_comment(db: Session, comment_id: int, comment_update: CommentUpdate) -> Optional[Comment]:
        db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not db_comment:
            return None
        
        update_data = comment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_comment, field, value)
        
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def delete_comment(db: Session, comment_id: int) -> bool:
        db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not db_comment:
            return False
        
        db.delete(db_comment)
        db.commit()
        return True

