from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os

from fastapi_sso.sso.github import GithubSSO

from src.database import get_db
from src.schemas.auth import (
    UserRegister, UserLogin, Token, TokenRefresh,
    RefreshSessionResponse, UserMe
)
from src.services.auth_service import AuthService
from src.dependencies.auth import get_current_user
from src.models.user import User

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

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user = await AuthService.register_user(
        db=db,
        name=user_data.name,
        email=user_data.email,
        password=user_data.password
    )
    
    user_agent = request.headers.get("user-agent")
    tokens = await AuthService.create_tokens_for_user(db, user, user_agent)
    
    return tokens

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user = await AuthService.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_agent = request.headers.get("user-agent")
    tokens = await AuthService.create_tokens_for_user(db, user, user_agent)
    
    return tokens

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_agent = request.headers.get("user-agent")
    tokens = await AuthService.refresh_tokens(db, token_data.refresh_token, user_agent)
    return tokens

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    await AuthService.logout(db, token_data.refresh_token)

@router.get("/me", response_model=UserMe)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/sessions", response_model=List[RefreshSessionResponse])
async def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    sessions = await AuthService.get_user_sessions(db, current_user.id)
    return sessions

@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await AuthService.logout_all_sessions(db, current_user.id)

@router.get("/github/login")
async def github_login():
    with github_sso:
        return await github_sso.get_login_redirect()

@router.get("/github/callback", response_model=Token)
async def github_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        with github_sso:
            user_data = await github_sso.verify_and_process(request)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="GitHub authentication failed"
            )
        
        user = await AuthService.get_or_create_github_user(
            db=db,
            github_id=str(user_data.id),
            email=user_data.email,
            name=user_data.display_name or user_data.email.split('@')[0],
            avatar=user_data.picture or ""
        )
        
        user_agent = request.headers.get("user-agent")
        tokens = await AuthService.create_tokens_for_user(db, user, user_agent)
        
        return tokens
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"GitHub authentication failed: {str(e)}"
        )

