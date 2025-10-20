from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.news import NewsCreate, NewsUpdate, NewsResponse
from src.services.news_service import NewsService
from src.dependencies.auth import (
    get_current_verified_author,
    get_news_with_permission,
    get_optional_current_user
)
from src.models.user import User
from src.models.news import News
from typing import List

router = APIRouter(prefix="/news", tags=["news"])

@router.post("/", response_model=NewsResponse, status_code=201)
def create_news(
    news: NewsCreate,
    current_user: User = Depends(get_current_verified_author),
    db: Session = Depends(get_db)
):
    news.author_id = current_user.id
    db_news = News(**news.model_dump())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

@router.get("/", response_model=List[NewsResponse])
def get_all_news(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    return NewsService.get_all_news(db, skip, limit)

@router.get("/{news_id}", response_model=NewsResponse)
def get_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    news = NewsService.get_news(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

@router.put("/{news_id}", response_model=NewsResponse)
def update_news(
    news_update: NewsUpdate,
    news: News = Depends(get_news_with_permission),
    db: Session = Depends(get_db)
):
    update_data = news_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(news, field, value)
    db.commit()
    db.refresh(news)
    return news

@router.delete("/{news_id}", status_code=204)
def delete_news(
    news: News = Depends(get_news_with_permission),
    db: Session = Depends(get_db)
):
    db.delete(news)
    db.commit()

