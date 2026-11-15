from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from time import perf_counter

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.api.v1 import auth, links
from app.core.config import settings
from app.core.logger import configure_logger
from app.db.cache import close_redis_pool, init_redis_pool

configure_logger()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await init_redis_pool()
    yield
    await close_redis_pool()


app = FastAPI(
    title="shortener-api-backend",
    description="URL shortener with JWT auth, Redis cache and Celery analytics",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def structlog_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    start = perf_counter()
    response = await call_next(request)
    duration_ms = round((perf_counter() - start) * 1000, 2)
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"service": "shortener-api", "docs": "/docs"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(links.router)
