from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    AUTHOR = "author"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_verified_author = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    github_id = Column(String, unique=True, nullable=True)

    news = relationship("News", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    refresh_sessions = relationship("RefreshSession", back_populates="user", cascade="all, delete-orphan")

