from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    news_id: int
    author_id: Optional[int] = None

class CommentUpdate(BaseModel):
    text: Optional[str] = None

class CommentResponse(CommentBase):
    id: int
    news_id: int
    author_id: int
    publication_date: datetime

    class Config:
        from_attributes = True

