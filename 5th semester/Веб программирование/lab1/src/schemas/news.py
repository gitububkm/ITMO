from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class NewsBase(BaseModel):
    title: str
    content: Dict[str, Any]
    cover: Optional[str] = None

class NewsCreate(NewsBase):
    author_id: Optional[int] = None

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    cover: Optional[str] = None

class NewsResponse(NewsBase):
    id: int
    publication_date: datetime
    author_id: int

    class Config:
        from_attributes = True

