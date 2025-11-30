from fastapi import APIRouter, Depends, HTTPException
from src.schemas.news import NewsCreate, NewsUpdate, NewsResponse
from src.services.news_service import NewsService
from src.dependencies.auth import (
    UserContext,
    get_current_verified_author,
    get_news_with_permission,
    get_optional_current_user,
)
from src.models.news import News
from typing import List

router = APIRouter(prefix="/news", tags=["news"])

from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

def get_news_service(db: AsyncSession = Depends(get_db)) -> NewsService:
    return NewsService(db)

@router.post("/", response_model=NewsResponse, status_code=201)
async def create_news(
    news: NewsCreate,
    current_user: UserContext = Depends(get_current_verified_author),
    service: NewsService = Depends(get_news_service)
):
    news.author_id = current_user.id
    created = await service.create(news)
    if not created:
        raise HTTPException(status_code=403, detail="Not allowed")
    return created

@router.get("/", response_model=List[NewsResponse])
async def get_all_news(
    skip: int = 0,
    limit: int = 100,
    _current_user: UserContext | None = Depends(get_optional_current_user),
    service: NewsService = Depends(get_news_service)
):
    return await service.list(skip, limit)

@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(
    news_id: int,
    _current_user: UserContext | None = Depends(get_optional_current_user),
    service: NewsService = Depends(get_news_service)
):
    news = await service.get(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(
    news_update: NewsUpdate,
    news: News = Depends(get_news_with_permission),
    service: NewsService = Depends(get_news_service)
):
    updated = await service.update(news.id, news_update)
    if not updated:
        raise HTTPException(status_code=404, detail="News not found")
    return updated

@router.delete("/{news_id}", status_code=204)
async def delete_news(
    news: News = Depends(get_news_with_permission),
    service: NewsService = Depends(get_news_service)
):
    await service.delete(news.id)

