from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.comment import Comment
from src.models.news import News
from src.models.user import User, UserRole
from src.services.auth_service import AuthService
from src.services.cache import SyncCacheService

security = HTTPBearer()


@dataclass(frozen=True)
class UserContext:
    id: int
    name: str
    email: str
    role: UserRole
    is_verified_author: bool
    avatar: Optional[str]
    registration_date: datetime


def _context_from_user(user: User) -> UserContext:
    return UserContext(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_verified_author=user.is_verified_author,
        avatar=user.avatar,
        registration_date=user.registration_date,
    )


def _context_from_cache(payload: dict) -> UserContext:
    registration_date = payload.get("registration_date")
    return UserContext(
        id=payload["id"],
        name=payload.get("name"),
        email=payload["email"],
        role=UserRole(payload["role"]),
        is_verified_author=payload["is_verified_author"],
        avatar=payload.get("avatar"),
        registration_date=datetime.fromisoformat(registration_date)
        if registration_date
        else datetime.utcnow(),
    )


def _cache_user_safe(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "is_verified_author": user.is_verified_author,
        "avatar": user.avatar,
        "registration_date": user.registration_date.isoformat()
        if user.registration_date
        else None,
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserContext:
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    if user_id is None or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    cache = SyncCacheService()
    cached = cache.get_user(int(user_id))
    if cached:
        return _context_from_cache(cached)
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    cache.set_user(user.id, _cache_user_safe(user))
    return _context_from_user(user)


def get_current_verified_author(
    current_user: UserContext = Depends(get_current_user)
) -> UserContext:
    if not current_user.is_verified_author and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only verified authors can perform this action"
        )
    return current_user


def get_current_admin(
    current_user: UserContext = Depends(get_current_user)
) -> UserContext:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_news_with_permission(
    news_id: int,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> News:
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )
    
    if current_user.role == UserRole.ADMIN:
        return news
    
    if news.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this news"
        )
    
    return news


async def get_comment_with_permission(
    comment_id: int,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Comment:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if current_user.role == UserRole.ADMIN:
        return comment
    
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this comment"
        )
    
    return comment


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserContext]:
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = AuthService.decode_token(token)
        
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            return None
        cache = SyncCacheService()
        cached = cache.get_user(int(user_id))
        if cached:
            return _context_from_cache(cached)
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        if user:
            cache.set_user(user.id, _cache_user_safe(user))
            return _context_from_user(user)
        return None
    except:
        return None

