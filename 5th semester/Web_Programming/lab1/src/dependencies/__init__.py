from src.dependencies.auth import (
    get_current_user,
    get_current_verified_author,
    get_current_admin,
    get_news_with_permission,
    get_comment_with_permission,
    get_optional_current_user
)

__all__ = [
    "get_current_user",
    "get_current_verified_author",
    "get_current_admin",
    "get_news_with_permission",
    "get_comment_with_permission",
    "get_optional_current_user"
]

