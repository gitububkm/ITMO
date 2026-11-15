import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.db.session import get_db_session
from app.models import User
from app.schemas import LinkCreate, LinkRead, LinkStats
from app.schemas.role import UserRole
from app.services import LinkService
from app.worker.tasks import record_click

router = APIRouter(tags=["links"])


@router.post("/api/v1/links", response_model=LinkRead, status_code=HTTPStatus.CREATED)
async def create_link(
    payload: LinkCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LinkRead:
    service = LinkService(session)
    try:
        link = await service.create_link(current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(exc)) from exc
    return LinkRead.model_validate(link)


@router.get("/api/v1/links", response_model=list[LinkRead])
async def list_links(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[LinkRead]:
    service = LinkService(session)
    include_all = current_user.role == UserRole.ADMIN
    links = await service.list_links(current_user, include_all=include_all)
    return [LinkRead.model_validate(link) for link in links]


@router.get("/api/v1/links/{link_id}/stats", response_model=LinkStats)
async def link_stats(
    link_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LinkStats:
    service = LinkService(session)
    try:
        stats = await service.get_stats(
            current_user,
            link_id,
            allow_admin=current_user.role == UserRole.ADMIN,
        )
    except LookupError as exc:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(exc)) from exc
    return LinkStats(**stats)


@router.delete("/api/v1/links/{link_id}", response_model=LinkRead)
async def deactivate_link(
    link_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LinkRead:
    service = LinkService(session)
    try:
        link = await service.deactivate(
            current_user,
            link_id,
            allow_admin=current_user.role == UserRole.ADMIN,
        )
    except LookupError as exc:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(exc)) from exc
    return LinkRead.model_validate(link)


@router.get("/r/{short_code}")
async def redirect_short_link(
    short_code: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    service = LinkService(session)
    link = await service.resolve_for_redirect(short_code)
    if link is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Link not found or expired")

    record_click.delay(
        str(link.id),
        referer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return RedirectResponse(url=link.original_url, status_code=HTTPStatus.FOUND)


@router.get("/api/v1/links/{short_code}/resolve")
async def resolve_link_info(
    short_code: str,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Debug/helper endpoint: returns short URL without redirect."""
    service = LinkService(session)
    link = await service.resolve_for_redirect(short_code)
    if link is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Link not found or expired")
    return {
        "short_code": link.short_code,
        "original_url": link.original_url,
        "short_url": f"{settings.BASE_URL.rstrip('/')}/r/{link.short_code}",
    }
