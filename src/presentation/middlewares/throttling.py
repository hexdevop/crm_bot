import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self._last_seen: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id: int | None = None
        if isinstance(event, Update):
            inner = event.event
            if hasattr(inner, "from_user") and inner.from_user:
                user_id = inner.from_user.id

        if user_id is not None:
            now = time.monotonic()
            if now - self._last_seen.get(user_id, 0.0) < self.rate_limit:
                return None
            self._last_seen[user_id] = now

        return await handler(event, data)
