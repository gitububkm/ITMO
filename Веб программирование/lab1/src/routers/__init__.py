from src.routers.users import router as users_router
from src.routers.news import router as news_router
from src.routers.comments import router as comments_router
from src.routers.auth import router as auth_router

__all__ = ["users_router", "news_router", "comments_router", "auth_router"]

