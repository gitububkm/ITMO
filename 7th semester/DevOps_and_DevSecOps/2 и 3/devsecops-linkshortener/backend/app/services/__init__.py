import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_short_code,
    hash_password,
    verify_password,
)
from app.db.cache import (
    cache_delete,
    cache_get,
    cache_set,
    get_refresh_token_user,
    link_cache_key,
    revoke_refresh_token,
    store_refresh_token,
)
from app.models import Click, Link, User
from app.schemas import LinkCreate, TokenPair, UserCreate
from app.schemas.role import UserRole


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register(self, payload: UserCreate) -> User:
        existing = await self.session.scalar(select(User).where(User.email == payload.email))
        if existing is not None:
            msg = "Email already registered"
            raise ValueError(msg)

        user = User(
            name=payload.name,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            role=UserRole.USER,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.session.scalar(select(User).where(User.email == email))
        if user is None or not verify_password(user.hashed_password, password):
            msg = "Invalid email or password"
            raise ValueError(msg)
        return user

    async def issue_tokens(self, user: User) -> TokenPair:
        access = create_access_token(str(user.id))
        refresh = create_refresh_token()
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        await store_refresh_token(str(user.id), refresh, ttl)
        return TokenPair(access_token=access, refresh_token=refresh)

    async def refresh(self, refresh_token: str) -> TokenPair:
        user_id = await get_refresh_token_user(refresh_token)
        if user_id is None:
            msg = "Invalid refresh token"
            raise ValueError(msg)

        user = await self.session.get(User, uuid.UUID(user_id))
        if user is None:
            msg = "User not found"
            raise ValueError(msg)

        await revoke_refresh_token(refresh_token)
        return await self.issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        await revoke_refresh_token(refresh_token)


class LinkService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _ensure_unique_code(self, code: str) -> None:
        exists = await self.session.scalar(select(Link.id).where(Link.short_code == code))
        if exists is not None:
            msg = "Short code already exists"
            raise ValueError(msg)

    async def create_link(self, owner: User, payload: LinkCreate) -> Link:
        if payload.custom_code:
            code = payload.custom_code
            await self._ensure_unique_code(code)
        else:
            code = generate_short_code()
            for _ in range(5):
                exists = await self.session.scalar(select(Link.id).where(Link.short_code == code))
                if exists is None:
                    break
                code = generate_short_code()
            else:
                msg = "Could not generate unique short code"
                raise RuntimeError(msg)

        link = Link(
            short_code=code,
            original_url=str(payload.original_url),
            title=payload.title,
            expires_at=payload.expires_at,
            owner_id=owner.id,
        )
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        await cache_set(link_cache_key(link.short_code), link.original_url)
        return link

    async def list_links(self, owner: User, *, include_all: bool = False) -> list[Link]:
        stmt = select(Link).order_by(Link.created_at.desc())
        if not include_all:
            stmt = stmt.where(Link.owner_id == owner.id)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def get_owned_link(self, owner: User, link_id: uuid.UUID, *, allow_admin: bool = False) -> Link:
        link = await self.session.get(Link, link_id)
        if link is None:
            msg = "Link not found"
            raise LookupError(msg)
        if link.owner_id != owner.id and not (allow_admin and owner.role == UserRole.ADMIN):
            msg = "Forbidden"
            raise PermissionError(msg)
        return link

    async def deactivate(self, owner: User, link_id: uuid.UUID, *, allow_admin: bool = False) -> Link:
        link = await self.get_owned_link(owner, link_id, allow_admin=allow_admin)
        link.is_active = False
        await self.session.commit()
        await self.session.refresh(link)
        await cache_delete(link_cache_key(link.short_code))
        return link

    async def resolve_for_redirect(self, short_code: str) -> Link | None:
        cached = await cache_get(link_cache_key(short_code))
        link = await self.session.scalar(select(Link).where(Link.short_code == short_code))
        if link is None:
            return None

        if not link.is_active:
            return None

        if link.expires_at is not None and link.expires_at <= datetime.now(UTC):
            link.is_active = False
            await self.session.commit()
            await cache_delete(link_cache_key(short_code))
            return None

        if cached is None:
            await cache_set(link_cache_key(short_code), link.original_url)

        return link

    async def get_stats(self, owner: User, link_id: uuid.UUID, *, allow_admin: bool = False) -> dict:
        link = await self.get_owned_link(owner, link_id, allow_admin=allow_admin)
        since = datetime.now(UTC) - timedelta(days=7)
        recent = await self.session.scalar(
            select(func.count()).select_from(Click).where(Click.link_id == link.id, Click.clicked_at >= since),
        )
        return {
            "short_code": link.short_code,
            "original_url": link.original_url,
            "click_count": link.click_count,
            "recent_clicks": int(recent or 0),
            "is_active": link.is_active,
            "created_at": link.created_at,
            "expires_at": link.expires_at,
        }
