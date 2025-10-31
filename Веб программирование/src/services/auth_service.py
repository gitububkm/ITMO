from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import os

from src.models.user import User, UserRole
from src.services.cache import SyncCacheService

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def register_user(db: AsyncSession, name: str, email: str, password: str) -> User:
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        password_hash = AuthService.get_password_hash(password)
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=UserRole.USER
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not user.password_hash:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def create_tokens_for_user(
        db: AsyncSession, 
        user: User, 
        user_agent: Optional[str] = None
    ) -> dict:
        access_token = AuthService.create_access_token(data={"sub": str(user.id)})
        refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
        
        # Храним сессию в Redis
        token_prefix = refresh_token[:16]
        session_data = {
            "user_id": user.id,
            "user_agent": user_agent,
            "created_at": datetime.utcnow().isoformat(),
        }
        SyncCacheService().set_session(user.id, token_prefix, session_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def refresh_tokens(db: AsyncSession, refresh_token: str, user_agent: Optional[str] = None) -> dict:
        payload = AuthService.decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = int(payload.get("sub"))
        token_prefix = refresh_token[:16]
        cache = SyncCacheService()
        session = cache.get_session(user_id, token_prefix)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Удаляем старую сессию и создаем новую
        cache.delete_session(user_id, token_prefix)
        return await AuthService.create_tokens_for_user(db, user, user_agent)

    @staticmethod
    async def logout(db: AsyncSession, refresh_token: str) -> bool:
        try:
            payload = AuthService.decode_token(refresh_token)
            user_id = int(payload.get("sub"))
            token_prefix = refresh_token[:16]
            SyncCacheService().delete_session(user_id, token_prefix)
            return True
        except Exception:
            return False

    @staticmethod
    async def get_user_sessions(db: AsyncSession, user_id: int):
        # Не реализовано — для Redis требуется отдельный трекинг ключей
        return []

    @staticmethod
    async def logout_all_sessions(db: AsyncSession, user_id: int) -> int:
        # Можно реализовать через хранение списка префиксов на пользователя
        return 0

    @staticmethod
    async def get_or_create_github_user(db: AsyncSession, github_id: str, email: str, name: str, avatar: str) -> User:
        result = await db.execute(select(User).where(User.github_id == github_id))
        user = result.scalar_one_or_none()
        
        if user:
            return user
        
        result = await db.execute(select(User).where(User.email == email))
        existing_email_user = result.scalar_one_or_none()
        if existing_email_user:
            existing_email_user.github_id = github_id
            if not existing_email_user.avatar:
                existing_email_user.avatar = avatar
            await db.commit()
            await db.refresh(existing_email_user)
            return existing_email_user
        
        user = User(
            name=name,
            email=email,
            github_id=github_id,
            avatar=avatar,
            role=UserRole.USER
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

