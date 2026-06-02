from aiogram import Dispatcher
from loguru import logger

from . import main, search


def reg_routers(dp: Dispatcher):
    files = [main, search]
    for file in files:
        dp.include_router(file.router)

    logger.opt(colors=True).info(
        f"<fg #b4ffb4>[user.clients {len(files)} files imported]</>"
    )
