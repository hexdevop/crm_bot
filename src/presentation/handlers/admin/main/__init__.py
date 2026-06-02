from aiogram import Router
from loguru import logger

from src.presentation.filters.admin import IsAdminFilter
from . import admin


def reg_routers(router: Router):
    admin.router.message.filter(IsAdminFilter())
    router.include_router(admin.router)
    logger.opt(colors=True).info("<fg #ffb4aa>[admin.main 1 file imported]</>")
