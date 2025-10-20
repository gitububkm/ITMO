from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import os

from src.models.user import User, UserRole
from src.models.refresh_session import RefreshSession

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
    def register_user(db: Session, name: str, email: str, password: str) -> User:
        existing_user = db.query(User).filter(User.email == email).first()
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
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.password_hash:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_tokens_for_user(
        db: Session, 
        user: User, 
        user_agent: Optional[str] = None
    ) -> dict:
        access_token = AuthService.create_access_token(data={"sub": str(user.id)})
        refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
        
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_session = RefreshSession(
            user_id=user.id,
            refresh_token=refresh_token,
            user_agent=user_agent,
            expires_at=expires_at
        )
        db.add(refresh_session)
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str, user_agent: Optional[str] = None) -> dict:
        payload = AuthService.decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        session = db.query(RefreshSession).filter(
            RefreshSession.refresh_token == refresh_token
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        if session.expires_at < datetime.utcnow():
            db.delete(session)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        user = db.query(User).filter(User.id == session.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        db.delete(session)
        db.commit()
        
        return AuthService.create_tokens_for_user(db, user, user_agent)

    @staticmethod
    def logout(db: Session, refresh_token: str) -> bool:
        session = db.query(RefreshSession).filter(
            RefreshSession.refresh_token == refresh_token
        ).first()
        
        if session:
            db.delete(session)
            db.commit()
            return True
        return False

    @staticmethod
    def get_user_sessions(db: Session, user_id: int):
        return db.query(RefreshSession).filter(
            RefreshSession.user_id == user_id,
            RefreshSession.expires_at > datetime.utcnow()
        ).all()

    @staticmethod
    def logout_all_sessions(db: Session, user_id: int) -> int:
        sessions = db.query(RefreshSession).filter(
            RefreshSession.user_id == user_id
        ).all()
        count = len(sessions)
        for session in sessions:
            db.delete(session)
        db.commit()
        return count

    @staticmethod
    def get_or_create_github_user(db: Session, github_id: str, email: str, name: str, avatar: str) -> User:
        user = db.query(User).filter(User.github_id == github_id).first()
        
        if user:
            return user
        
        existing_email_user = db.query(User).filter(User.email == email).first()
        if existing_email_user:
            existing_email_user.github_id = github_id
            if not existing_email_user.avatar:
                existing_email_user.avatar = avatar
            db.commit()
            db.refresh(existing_email_user)
            return existing_email_user
        
        user = User(
            name=name,
            email=email,
            github_id=github_id,
            avatar=avatar,
            role=UserRole.USER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

