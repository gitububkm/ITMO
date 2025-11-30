import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_sso.sso.github import GithubSSO
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies.auth import UserContext, get_current_user
from src.schemas.auth import (
    RefreshSessionResponse,
    Token,
    TokenRefresh,
    UserLogin,
    UserMe,
    UserRegister,
)
from src.services.auth_service import AuthApplicationService

router = APIRouter(prefix="/auth", tags=["auth"])

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "mock_github_client_id")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "mock_github_client_secret")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback")

github_sso = GithubSSO(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    redirect_uri=GITHUB_REDIRECT_URI,
    allow_insecure_http=True
)

def get_auth_app_service(db: AsyncSession = Depends(get_db)) -> AuthApplicationService:
    return AuthApplicationService(db)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    service: AuthApplicationService = Depends(get_auth_app_service),
):
    user_agent = request.headers.get("user-agent")
    return await service.register(user_data, user_agent)


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    request: Request,
    service: AuthApplicationService = Depends(get_auth_app_service),
):
    user_agent = request.headers.get("user-agent")
    return await service.login(user_data, user_agent)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    request: Request,
    service: AuthApplicationService = Depends(get_auth_app_service),
):
    user_agent = request.headers.get("user-agent")
    return await service.refresh(token_data.refresh_token, user_agent)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token_data: TokenRefresh,
    service: AuthApplicationService = Depends(get_auth_app_service),
):
    await service.logout(token_data.refresh_token)

@router.get("/me", response_model=UserMe)
def get_me(current_user: UserContext = Depends(get_current_user)):
    return current_user

@router.get("/sessions", response_model=List[RefreshSessionResponse])
async def get_my_sessions(
    current_user: UserContext = Depends(get_current_user),
    service: AuthApplicationService = Depends(get_auth_app_service),
):
    return await service.list_sessions(current_user.id)

@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all_sessions(
    current_user: UserContext = Depends(get_current_user),
    service: AuthApplicationService = Depends(get_auth_app_service),
):
    await service.logout_all_sessions(current_user.id)

@router.get("/github/login")
async def github_login():
    with github_sso:
        return await github_sso.get_login_redirect()

@router.get("/github/callback", response_model=Token)
async def github_callback(
    request: Request,
    service: AuthApplicationService = Depends(get_auth_app_service),
):
    try:
        with github_sso:
            user_data = await github_sso.verify_and_process(request)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="GitHub authentication failed"
            )
        
        user_agent = request.headers.get("user-agent")
        return await service.tokens_for_github_user(
            github_id=str(user_data.id),
            email=user_data.email,
            name=user_data.display_name or user_data.email.split('@')[0],
            avatar=user_data.picture or "",
            user_agent=user_agent,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"GitHub authentication failed: {str(e)}"
        )

