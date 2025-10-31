from __future__ import annotations
import json
import logging
from typing import Any, Optional
import os
import redis

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
NEWS_CACHE_TTL = int(os.getenv("NEWS_CACHE_TTL", "300"))  # 5 минут
USER_CACHE_TTL = int(os.getenv("USER_CACHE_TTL", "600"))  # 10 минут
SESSION_CACHE_TTL = int(os.getenv("SESSION_CACHE_TTL", "2592000"))  # 30 дней

class SyncCacheService:
    def __init__(self) -> None:
        self.client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value is None:
                logger.info(f"cache_miss key={key}")
                return None
            logger.info(f"cache_hit key={key}")
            return json.loads(value)
        except Exception as exc:
            logger.error(f"cache_get_error key={key} err={exc}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            payload = json.dumps(value, default=str)
            if ttl:
                self.client.setex(key, ttl, payload)
            else:
                self.client.set(key, payload)
            logger.info(f"cache_set key={key} ttl={ttl}")
            return True
        except Exception as exc:
            logger.error(f"cache_set_error key={key} err={exc}")
            return False

    def delete(self, key: str) -> bool:
        try:
            self.client.delete(key)
            logger.info(f"cache_del key={key}")
            return True
        except Exception as exc:
            logger.error(f"cache_del_error key={key} err={exc}")
            return False

    # Логические ключи
    def get_news(self, news_id: int) -> Optional[dict]:
        return self.get(f"news:{news_id}")

    def set_news(self, news_id: int, data: dict) -> bool:
        return self.set(f"news:{news_id}", data, NEWS_CACHE_TTL)

    def get_news_list(self, skip: int, limit: int) -> Optional[list]:
        return self.get(f"news_list:{skip}:{limit}")

    def set_news_list(self, skip: int, limit: int, data: list) -> bool:
        return self.set(f"news_list:{skip}:{limit}", data, NEWS_CACHE_TTL)

    def get_user(self, user_id: int) -> Optional[dict]:
        return self.get(f"user:{user_id}")

    def set_user(self, user_id: int, data: dict) -> bool:
        return self.set(f"user:{user_id}", data, USER_CACHE_TTL)

    def set_session(self, user_id: int, token_prefix: str, data: dict) -> bool:
        return self.set(f"session:{user_id}:{token_prefix}", data, SESSION_CACHE_TTL)

    def get_session(self, user_id: int, token_prefix: str) -> Optional[dict]:
        return self.get(f"session:{user_id}:{token_prefix}")

    def delete_session(self, user_id: int, token_prefix: str) -> bool:
        return self.delete(f"session:{user_id}:{token_prefix}")
