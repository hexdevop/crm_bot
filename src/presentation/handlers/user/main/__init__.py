from aiogram import Dispatcher
from loguru import logger

from . import start, lang


def reg_routers(dp: Dispatcher):
    files = [start, lang]
    for file in files:
        dp.include_router(file.router)
    logger.opt(colors=True).info(f"<fg #abffaa>[user.main {len(files)} files imported]</>")
