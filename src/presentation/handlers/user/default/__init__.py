from aiogram import Dispatcher
from aiogram.enums import ChatType
from loguru import logger

from src.presentation.filters.chat_type import ChatTypeFilter

from . import (
    status,
)


def reg_routers(dp: Dispatcher):
    handlers = [
        status,
    ]
    for handler in handlers:
        handler.router.message.filter(ChatTypeFilter(ChatType.PRIVATE))

        dp.include_router(handler.router)
    logger.opt(colors=True).info(
        f"<fg #abffaa>[user.default {len(handlers)} files imported]</>"
    )
