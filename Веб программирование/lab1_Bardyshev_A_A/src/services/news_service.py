from sqlalchemy.orm import Session
from src.models.news import News
from src.models.user import User
from src.schemas.news import NewsCreate, NewsUpdate
from typing import List, Optional

class NewsService:
    @staticmethod
    def create_news(db: Session, news: NewsCreate) -> Optional[News]:
        author = db.query(User).filter(User.id == news.author_id).first()
        if not author or not author.is_verified_author:
            return None
        
        db_news = News(**news.model_dump())
        db.add(db_news)
        db.commit()
        db.refresh(db_news)
        return db_news

    @staticmethod
    def get_news(db: Session, news_id: int) -> Optional[News]:
        return db.query(News).filter(News.id == news_id).first()

    @staticmethod
    def get_all_news(db: Session, skip: int = 0, limit: int = 100) -> List[News]:
        return db.query(News).offset(skip).limit(limit).all()

    @staticmethod
    def update_news(db: Session, news_id: int, news_update: NewsUpdate) -> Optional[News]:
        db_news = db.query(News).filter(News.id == news_id).first()
        if not db_news:
            return None
        
        update_data = news_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_news, field, value)
        
        db.commit()
        db.refresh(db_news)
        return db_news

    @staticmethod
    def delete_news(db: Session, news_id: int) -> bool:
        db_news = db.query(News).filter(News.id == news_id).first()
        if not db_news:
            return False
        
        db.delete(db_news)
        db.commit()
        return True

