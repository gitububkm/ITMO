from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_verified_author: bool = False
    avatar: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_verified_author: Optional[bool] = None
    avatar: Optional[str] = None

class UserResponse(UserBase):
    id: int
    registration_date: datetime

    class Config:
        from_attributes = True

