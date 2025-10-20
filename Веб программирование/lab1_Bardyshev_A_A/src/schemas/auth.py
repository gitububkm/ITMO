from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from src.models.user import UserRole

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class RefreshSessionResponse(BaseModel):
    id: int
    user_agent: Optional[str]
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

class UserMe(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    is_verified_author: bool
    avatar: Optional[str]
    registration_date: datetime

    class Config:
        from_attributes = True

