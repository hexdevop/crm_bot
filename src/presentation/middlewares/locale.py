from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram_i18n import I18nContext
from src.infrastructure.repo.user import UserRepository


class UserLocaleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        i18n: I18nContext | None = data.get("i18n")
        user_repo: UserRepository | None = data.get("user_repo")
        from_user = data.get("event_from_user")

        if i18n and user_repo and from_user:
            lang = await user_repo.get_language(from_user.id)
            if lang and lang in i18n.core.available_locales:
                i18n.locale = lang

        return await handler(event, data)


class AdminLocaleMiddleware(BaseMiddleware):
    def __init__(self, default_locale: str = "ru"):
        self.default_locale = default_locale

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        i18n: I18nContext | None = data.get("i18n")
        if i18n:
            i18n.locale = self.default_locale
        return await handler(event, data)
