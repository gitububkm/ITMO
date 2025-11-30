from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SYNC_DATABASE_URL: str | None = None
    REDIS_URL: str = "redis://localhost:6379"
    NEWS_CACHE_TTL: int = 300  # 5 minutes in seconds
    USER_CACHE_TTL: int = 600  # 10 minutes for users
    SESSION_CACHE_TTL: int = 2592000  # 30 days in seconds (same as refresh token)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
