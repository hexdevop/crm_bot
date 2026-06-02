from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.infrastructure.db.main import session_maker
from src.infrastructure.repo.user import UserRepository
from src.infrastructure.repo.client import ClientRepository
from src.infrastructure.repo.server import ServerRepository
from src.infrastructure.repo.bot import BotRepository
from src.application.services.user_service import UserService
from src.infrastructure.cache.manager import cache_manager
from src.domain.user import User
from src.domain.client import Client
from src.domain.server import Server
from src.domain.bot import TgBot


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with session_maker() as session:
            user_repo = UserRepository(session, User, cache_manager)
            client_repo = ClientRepository(session, Client, cache_manager)
            server_repo = ServerRepository(session, Server, cache_manager)
            bot_repo = BotRepository(session, TgBot, cache_manager)

            data["cache_manager"] = cache_manager
            data["session"] = session
            data["user_repo"] = user_repo
            data["user_service"] = UserService(user_repo)
            data["client_repo"] = client_repo
            data["server_repo"] = server_repo
            data["bot_repo"] = bot_repo

            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
