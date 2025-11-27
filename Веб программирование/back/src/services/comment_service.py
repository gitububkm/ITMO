from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment
from src.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_comment(self, comment: CommentCreate) -> Comment:
        db_comment = Comment(**comment.model_dump())
        self.db.add(db_comment)
        await self.db.commit()
        await self.db.refresh(db_comment)
        return db_comment

    async def get_comment(self, comment_id: int) -> Optional[Comment]:
        result = await self.db.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalar_one_or_none()

    async def get_comments(self, skip: int = 0, limit: int = 100) -> List[Comment]:
        result = await self.db.execute(
            select(Comment).order_by(Comment.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_comments_by_news(self, news_id: int) -> List[Comment]:
        result = await self.db.execute(select(Comment).where(Comment.news_id == news_id))
        return list(result.scalars().all())

    async def update_comment(
        self,
        comment_id: int,
        comment_update: CommentUpdate,
    ) -> Optional[Comment]:
        db_comment = await self.get_comment(comment_id)
        if not db_comment:
            return None

        update_data = comment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_comment, field, value)

        await self.db.commit()
        await self.db.refresh(db_comment)
        return db_comment

    async def delete_comment(self, comment_id: int) -> bool:
        db_comment = await self.get_comment(comment_id)
        if not db_comment:
            return False

        await self.db.delete(db_comment)
        await self.db.commit()
        return True

