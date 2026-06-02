import time
import decimal
import orjson
from typing import Any
from redis.asyncio import Redis, from_url
from cachetools import TTLCache
from src.core.config import settings
from src.core.logger import logger

_FAILURE_THRESHOLD = 5
_CIRCUIT_RESET_SECONDS = 60


class CacheManager:
    def __init__(self):
        self.l1_cache = TTLCache(maxsize=1000, ttl=60)
        self.redis: Redis | None = None
        self._failures = 0
        self._circuit_open_until: float = 0.0

    def _redis_available(self) -> bool:
        if not self.redis:
            return False
        if time.monotonic() < self._circuit_open_until:
            return False
        return True

    def _record_success(self):
        self._failures = 0
        self._circuit_open_until = 0.0

    def _record_failure(self, op: str, exc: Exception):
        self._failures += 1
        logger.error(
            f"Redis error in {op} ({self._failures}/{_FAILURE_THRESHOLD}): {exc}"
        )
        if self._failures >= _FAILURE_THRESHOLD:
            self._circuit_open_until = time.monotonic() + _CIRCUIT_RESET_SECONDS
            self._failures = 0
            logger.warning(
                f"Redis circuit opened, pausing for {_CIRCUIT_RESET_SECONDS}s"
            )

    async def connect(self):
        try:
            self.redis = from_url(
                settings.redis_cache_url, encoding="utf-8", decode_responses=False
            )
            await self.redis.ping()
            logger.info("Connected to Redis (Cache)")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None

    async def close(self):
        if self.redis:
            await self.redis.aclose()

    async def get(self, key: str) -> Any | None:
        if key in self.l1_cache:
            return self.l1_cache[key]

        if self._redis_available():
            try:
                data = await self.redis.get(key)
                self._record_success()
                if data:
                    value = orjson.loads(data)
                    self.l1_cache[key] = value
                    return value
            except Exception as e:
                self._record_failure("get", e)
        return None

    @staticmethod
    def _serialize(value: Any) -> bytes:
        def default(obj):
            if isinstance(obj, decimal.Decimal):
                return int(obj) if obj == obj.to_integral_value() else float(obj)
            raise TypeError(f"Type is not JSON serializable: {type(obj)}")

        return orjson.dumps(value, default=default)

    async def set(self, key: str, value: Any, ttl: int = 300):
        self.l1_cache[key] = value

        if self._redis_available():
            try:
                await self.redis.set(key, self._serialize(value), ex=ttl)
                self._record_success()
            except Exception as e:
                self._record_failure("set", e)

    async def delete(self, key: str):
        self.l1_cache.pop(key, None)

        if self._redis_available():
            try:
                await self.redis.delete(key)
                self._record_success()
            except Exception as e:
                self._record_failure("delete", e)

    async def delete_pattern(self, pattern: str):
        import fnmatch

        for k in list(self.l1_cache.keys()):
            if fnmatch.fnmatch(k, pattern):
                del self.l1_cache[k]

        if self._redis_available():
            try:
                cursor = 0
                while True:
                    cursor, keys = await self.redis.scan(
                        cursor, match=pattern, count=100
                    )
                    if keys:
                        await self.redis.delete(*keys)
                    if cursor == 0:
                        break
                self._record_success()
            except Exception as e:
                self._record_failure("delete_pattern", e)


cache_manager = CacheManager()
