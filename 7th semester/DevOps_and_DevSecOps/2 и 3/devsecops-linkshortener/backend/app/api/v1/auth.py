from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models import User
from app.schemas import RefreshRequest, TokenPair, UserCreate, UserRead
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=HTTPStatus.CREATED)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_db_session)) -> User:
    service = AuthService(session)
    try:
        return await service.register(payload)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenPair)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> TokenPair:
    service = AuthService(session)
    try:
        user = await service.authenticate(form_data.username, form_data.password)
        return await service.issue_tokens(user)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_db_session)) -> TokenPair:
    service = AuthService(session)
    try:
        return await service.refresh(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout(payload: RefreshRequest, session: AsyncSession = Depends(get_db_session)) -> None:
    service = AuthService(session)
    await service.logout(payload.refresh_token)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
