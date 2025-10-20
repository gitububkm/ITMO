from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User, UserRole
from src.models.news import News
from src.models.comment import Comment
from src.services.auth_service import AuthService

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
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
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_verified_author(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_verified_author and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only verified authors can perform this action"
        )
    return current_user

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_news_with_permission(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> News:
    news = db.query(News).filter(News.id == news_id).first()
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

def get_comment_with_permission(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Comment:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
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

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = AuthService.decode_token(token)
        
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            return None
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except:
        return None

