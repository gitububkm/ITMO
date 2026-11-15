import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    role: str
    registered_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LinkCreate(BaseModel):
    original_url: HttpUrl
    title: str | None = Field(default=None, max_length=200)
    custom_code: str | None = Field(default=None, min_length=4, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    expires_at: datetime | None = None


class LinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    short_code: str
    original_url: str
    title: str | None
    click_count: int
    is_active: bool
    created_at: datetime
    expires_at: datetime | None
    owner_id: uuid.UUID


class LinkStats(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    recent_clicks: int
    is_active: bool
    created_at: datetime
    expires_at: datetime | None


class ClickRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    link_id: uuid.UUID
    clicked_at: datetime
    referer: str | None
    user_agent: str | None
    ip_hash: str | None
