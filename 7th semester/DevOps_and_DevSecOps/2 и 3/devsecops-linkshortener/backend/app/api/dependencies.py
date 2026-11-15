import uuid
from collections.abc import AsyncGenerator
from http import HTTPStatus

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session
from app.models import User
from app.schemas.role import UserRole

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token")
        user_id = uuid.UUID(subject)
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token") from exc

    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="User not found")
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Admin only")
    return user


async def get_db() -> AsyncGenerator[AsyncSession]:
    async for session in get_db_session():
        yield session
