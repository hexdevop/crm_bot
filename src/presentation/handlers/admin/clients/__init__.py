from aiogram import Router
from loguru import logger

from src.presentation.filters.admin import IsAdminFilter
from . import main, add, edit


def reg_routers(router: Router):
    files = [main, add, edit]
    for file in files:
        file.router.message.filter(IsAdminFilter())
        router.include_router(file.router)

    logger.opt(colors=True).info(
        f"<fg #ffb4aa>[admin.clients {len(files)} files imported]</>"
    )
