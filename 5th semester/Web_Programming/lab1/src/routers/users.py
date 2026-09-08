from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies.auth import UserContext, get_current_admin, get_optional_current_user
from src.schemas.user import UserCreate, UserResponse, UserUpdate
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    _current_user: UserContext = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(user)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    _current_user: UserContext | None = Depends(get_optional_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.get_users(skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    _current_user: UserContext | None = Depends(get_optional_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserContext = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    user = await service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: UserContext = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    if not await service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

